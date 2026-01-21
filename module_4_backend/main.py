"""
FastAPI Main Application for Secure RAG Chatbot
Module 4: Backend & Authentication
"""

import os
import sys
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from contextlib import asynccontextmanager

# Add parent directory to path to import Module 3
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database import engine, get_db, Base
from models import User, QueryLog, Conversation, ChatMessage
from schemas import (
    UserCreate, UserLogin, TokenResponse, TokenRefresh,
    RAGQueryRequest, RAGQueryResponse, UserStatsResponse, SourceInfo,
    ModelConfigRequest, ModelConfigResponse,
    ConversationCreate, ConversationResponse, ConversationDetailResponse,
    ChatMessageCreate, ChatMessageResponse, ConversationUpdateTitle
)
from auth import (
    create_access_token, create_refresh_token,
    verify_access_token, verify_refresh_token, get_password_hash, verify_password
)
from rbac import check_permission, get_user_role_permissions
import json
from query_processor import QueryProcessor

# Import Vector Database components
from vector_database.vector_db_manager import VectorDBManager
from vector_database.embedding_generator import EmbeddingGenerator

# Import LLM Integration components (Advanced RAG Pipeline)
from llm_integration.advanced_rag_pipeline import AdvancedRAGPipeline
from llm_integration.config import LLMConfig

# Security
security = HTTPBearer()

# Global instances
vector_db_manager = None
embedding_generator = None
query_processor = None
advanced_rag_pipeline = None  # Module 5: Advanced RAG Pipeline

# Model configurations per user (in-memory storage)
# In production, this should be stored in database
user_model_configs = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    global vector_db_manager, embedding_generator, query_processor, advanced_rag_pipeline
    
    # Startup: Initialize database and Module 3 components
    print("🚀 Starting up RAG Chatbot Backend...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Initialize Vector Database components
    vector_db_dir = os.path.join(os.path.dirname(__file__), '..', 'vector_database')
    chroma_path = os.path.join(vector_db_dir, 'chroma_db')
    
    embedding_generator = EmbeddingGenerator()
    vector_db_manager = VectorDBManager(persist_directory=chroma_path)
    query_processor = QueryProcessor()
    
    print(f"✅ Vector DB loaded from: {chroma_path}")
    
    # Verify vector DB has documents
    try:
        test_results = vector_db_manager.search(
            query_embedding=embedding_generator.generate_embedding("test"),
            n_results=1
        )
        doc_count = test_results.get('count', 0)
        print(f"✅ Vector DB contains {doc_count} documents")
    except Exception as e:
        print(f"⚠️ Warning: Could not verify vector DB: {e}")
    
    # Initialize Module 5: Advanced RAG Pipeline
    try:
        advanced_rag_pipeline = AdvancedRAGPipeline(
            enable_reranking=True,
            enable_confidence=True
        )
        print(f"✅ Advanced RAG Pipeline initialized")
    except Exception as e:
        print(f"⚠️ Warning: Advanced RAG Pipeline initialization failed: {e}")
        print("   Falling back to basic RAG mode")
        advanced_rag_pipeline = None
    
    print("✅ Backend startup complete!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down RAG Chatbot Backend...")


# Initialize FastAPI app
app = FastAPI(
    title="Secure RAG Chatbot API",
    description="Role-Based Access Control + Retrieval Augmented Generation",
    version="1.0.0",
    lifespan=lifespan
)


# ==================== Dependency Functions ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """Validate JWT token and return current user"""
    token = credentials.credentials
    
    try:
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )


def require_permission(permission: str):
    """Dependency to check if user has required permission"""
    async def permission_checker(user: User = Depends(get_current_user)) -> User:
        if not check_permission(user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return user
    return permission_checker


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Secure RAG Chatbot API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with system status"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "vector_db": vector_db_manager is not None,
            "embedding_generator": embedding_generator is not None,
            "query_processor": query_processor is not None,
            "advanced_rag_pipeline": advanced_rag_pipeline is not None
        }
    }
    
    # Add LLM provider info if advanced pipeline is available
    if advanced_rag_pipeline:
        health_status["llm_provider"] = advanced_rag_pipeline.llm_manager.provider.value
        health_status["llm_model"] = "meta-llama/Llama-3.2-3B-Instruct"  # Default model
    
    return health_status


@app.post("/auth/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user (role validation is done by Pydantic schema)
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "username": new_user.username,
        "role": new_user.role
    }


@app.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    User login - returns access and refresh tokens
    """
    # Find user
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        role=user.role
    )


@app.post("/auth/refresh", response_model=dict)
async def refresh_access_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    """
    try:
        payload = verify_refresh_token(token_data.refresh_token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        new_access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not refresh token: {str(e)}"
        )


@app.post("/query", response_model=RAGQueryResponse)
async def rag_query(
    query_request: RAGQueryRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    RAG Query Endpoint with RBAC
    
    Process:
    1. Normalize and process user query
    2. Generate embedding for query
    3. Search vector DB with RBAC filtering
    4. Construct prompt with retrieved context
    5. Generate response using LLM (simulated)
    6. Log query
    7. Return response with source attribution
    """
    try:
        # 1. Process query
        processed_query = query_processor.process_query(query_request.query)
        
        # 2. Generate embedding
        query_embedding = embedding_generator.generate_embedding(processed_query)
        
        # 3. Search vector DB with RBAC filtering
        search_results = vector_db_manager.search(
            query_embedding=query_embedding,
            n_results=query_request.top_k,
            user_role=user.role
        )
        
        # Extract documents and metadata
        documents = search_results.get('documents', [])
        metadatas = search_results.get('metadatas', [])
        distances = search_results.get('distances', [])
        
        if not documents:
            return RAGQueryResponse(
                query=query_request.query,
                processed_query=processed_query,
                answer="I don't have access to relevant information to answer your question based on your role permissions.",
                sources=[],
                metadata={
                    "user_role": user.role,
                    "documents_found": 0,
                    "model_used": "none"
                }
            )
        
        # 4. Construct prompt with context
        context_parts = []
        sources_info = []
        
        for idx, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
            context_parts.append(f"[Source {idx+1}]\n{doc}")
            
            # Calculate relevance score (convert distance to similarity)
            relevance_score = round(max(0, 1 - dist), 4)
            
            sources_info.append(SourceInfo(
                source_id=f"source_{idx+1}",
                document_name=meta.get('source', 'Unknown'),
                department=meta.get('department', 'Unknown'),
                chunk_index=meta.get('chunk_index', 0),
                relevance_score=relevance_score,
                content_preview=doc[:200] + "..." if len(doc) > 200 else doc
            ))
        
        context = "\n\n".join(context_parts)
        
        # Construct full prompt
        prompt = f"""You are a helpful AI assistant for an organization. Answer the user's question based ONLY on the provided context.

Context:
{context}

User Question: {query_request.query}

Instructions:
- Answer based strictly on the context provided
- If the context doesn't contain relevant information, say so
- Be concise and accurate
- Cite sources when applicable

Answer:"""
        
        # 5. Generate response (Simulated LLM - in production, use OpenAI/other LLM)
        # For now, we'll create a simple extractive answer
        answer = generate_answer_from_context(query_request.query, documents, metadatas)
        
        # 6. Log query
        query_log = QueryLog(
            user_id=user.id,
            query=query_request.query,
            processed_query=processed_query,
            response=answer,
            sources_accessed=len(documents),
            timestamp=datetime.utcnow()
        )
        db.add(query_log)
        db.commit()
        
        # 7. Return response
        return RAGQueryResponse(
            query=query_request.query,
            processed_query=processed_query,
            answer=answer,
            sources=sources_info,
            metadata={
                "user_role": user.role,
                "documents_found": len(documents),
                "model_used": "simulated_llm",
                "prompt_tokens": len(prompt.split()),
                "top_k": query_request.top_k
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@app.post("/query/advanced", response_model=dict)
async def advanced_rag_query(
    query_request: RAGQueryRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Advanced RAG Query Endpoint with LLM Integration (Module 5)
    
    Features:
    - Real LLM integration (HuggingFace/OpenAI)
    - Document re-ranking
    - Enhanced response formatting
    - Confidence scoring
    - Better citation tracking
    
    Process:
    1. Validate advanced pipeline is available
    2. Process query through advanced RAG pipeline
    3. Log query with enhanced metadata
    4. Return response with confidence scores
    """
    try:
        # Check if advanced pipeline is available
        if advanced_rag_pipeline is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Advanced RAG pipeline not available. Please check LLM configuration."
            )
        
        # Set user-configured API key if available (from UI)
        user_config = user_model_configs.get(user.id)
        if user_config and user_config.get('api_key'):
            provider = user_config.get('model_provider', 'huggingface')
            api_key = user_config.get('api_key')
            
            # Temporarily set environment variable for this user's request
            if provider == 'openai':
                os.environ['OPENAI_API_KEY'] = api_key
                print(f"🔑 Using user-provided OpenAI API key for {user.username}")
            elif provider == 'huggingface':
                os.environ['HUGGINGFACE_API_KEY'] = api_key
                print(f"🔑 Using user-provided HuggingFace API key for {user.username}")
            elif provider == 'ollama':
                print(f"🦙 Using Ollama model: {user_config.get('model_name', 'default')}")
            
            # Reinitialize the LLM manager with the new API key
            try:
                from module_5_llm_integration.advanced_rag_pipeline import AdvancedRAGPipeline
                temp_pipeline = AdvancedRAGPipeline(
                    llm_provider=provider,
                    enable_reranking=True,
                    enable_confidence=True
                )
                print(f"✅ Created temporary pipeline with {provider} for user {user.username}")
            except Exception as e:
                print(f"⚠️ Failed to create user-specific pipeline: {e}")
                temp_pipeline = advanced_rag_pipeline
        else:
            # Use the default global pipeline
            temp_pipeline = advanced_rag_pipeline
            print(f"ℹ️ Using default pipeline for {user.username}")
        
        # Step 1: Process query and generate embedding
        processed_query = query_processor.process_query(query_request.query)
        query_embedding = embedding_generator.generate_embedding(processed_query)
        
        # Step 2: Retrieve documents from vector DB with RBAC
        search_results = vector_db_manager.search(
            query_embedding=query_embedding,
            n_results=query_request.top_k,
            user_role=user.role
        )
        
        # Step 3: Convert retrieved results to chunks for advanced pipeline
        chunks = []
        documents = search_results.get('documents', [])
        metadatas = search_results.get('metadatas', [])
        distances = search_results.get('distances', [])
        ids = search_results.get('ids', [])
        
        # Debug: Log first metadata to see structure
        if metadatas and len(metadatas) > 0:
            print(f"📊 Sample metadata: {metadatas[0]}")
        
        for i, (doc, meta, dist, doc_id) in enumerate(zip(documents, metadatas, distances, ids)):
            chunks.append({
                'chunk_id': doc_id,
                'id': doc_id,  # Add 'id' field for compatibility
                'text': doc,
                'score': max(0, 1 - dist),  # Convert distance to similarity
                'department': meta.get('department', 'Unknown'),
                'source_file': meta.get('source', meta.get('source_file', 'Unknown')),
                'chunk_index': meta.get('chunk_index', i)
            })
        
        # Get accessible departments for metadata
        accessible_departments = list(set([chunk['department'] for chunk in chunks]))
        
        # Step 4: Process through advanced RAG pipeline (use user-specific or default)
        pipeline_response = temp_pipeline.process_query(
            query=query_request.query,
            retrieved_chunks=chunks,
            user_role=user.role,
            accessible_departments=accessible_departments,
            metadata={'processed_query': processed_query}
        )
        
        # Extract response data
        answer = pipeline_response.get('answer', '')
        sources = pipeline_response.get('sources', [])
        confidence = pipeline_response.get('confidence', {})
        response_metadata = pipeline_response.get('metadata', {})
        
        # Convert sources to SourceInfo format
        sources_info = []
        for source in sources:
            sources_info.append(SourceInfo(
                source_id=source.get('id', 'unknown'),
                document_name=source.get('source_file', 'Unknown'),
                department=source.get('department', 'Unknown'),
                chunk_index=source.get('chunk_index', 0),
                relevance_score=source.get('relevance_score', 0.0),
                content_preview=source.get('preview', '')[:200]
            ))
        
        # Log query with advanced metadata
        query_log = QueryLog(
            user_id=user.id,
            query=query_request.query,
            processed_query=response_metadata.get('processed_query', processed_query),
            response=answer,
            sources_accessed=len(sources),
            timestamp=datetime.utcnow()
        )
        db.add(query_log)
        db.commit()
        
        # Return enhanced response
        from schemas import ConfidenceMetrics, AdvancedRAGResponse
        
        # Extract confidence metrics properly
        components = confidence.get('components', {})
        confidence_metrics = ConfidenceMetrics(
            overall_confidence=confidence.get('overall_confidence', 0.0),
            retrieval_quality=components.get('retrieval_quality', 0.0),
            citation_coverage=components.get('citation_coverage', 0.0),
            answer_completeness=components.get('answer_completeness', 0.0),
            confidence_level=confidence.get('confidence_level', 'low')
        )
        
        return {
            "query": query_request.query,
            "processed_query": response_metadata.get('processed_query', processed_query),
            "answer": answer,
            "sources": [s.dict() for s in sources_info],
            "confidence": confidence_metrics.dict(),
            "metadata": {
                **response_metadata,
                "user_role": user.role,
                "pipeline": "advanced_rag_v1",
                "documents_found": len(sources)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ Advanced RAG Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing advanced query: {str(e)}"
        )


@app.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user statistics and query history
    """
    # Get user's query logs
    query_logs = db.query(QueryLog).filter(QueryLog.user_id == user.id).all()
    
    # Calculate stats
    total_queries = len(query_logs)
    
    # Get permissions for user role
    permissions = get_user_role_permissions(user.role)
    
    # Get accessible departments using RBAC function
    from rbac import get_effective_roles
    accessible_departments = get_effective_roles(user.role)
    
    # Get recent queries (last 10)
    recent_queries = db.query(QueryLog).filter(
        QueryLog.user_id == user.id
    ).order_by(QueryLog.timestamp.desc()).limit(10).all()
    
    recent_queries_list = [
        {
            "query": log.query,
            "timestamp": log.timestamp.isoformat(),
            "sources_accessed": log.sources_accessed
        }
        for log in recent_queries
    ]
    
    return UserStatsResponse(
        user_id=user.id,
        username=user.username,
        role=user.role,
        total_queries=total_queries,
        permissions=permissions,
        accessible_departments=accessible_departments,
        recent_queries=recent_queries_list,
        account_created=user.created_at.isoformat() if user.created_at else None,
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@app.get("/admin/users", dependencies=[Depends(require_permission("manage_users"))])
async def list_users(db: Session = Depends(get_db)):
    """
    Admin only: List all users
    """
    users = db.query(User).all()
    return {
        "total_users": len(users),
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            for user in users
        ]
    }


@app.post("/config/model", response_model=ModelConfigResponse)
async def configure_model(
    config: ModelConfigRequest,
    user: User = Depends(get_current_user)
):
    """
    Configure LLM model settings for the user
    Stores model provider, API keys, and model selection preferences
    """
    try:
        # Store configuration in memory (indexed by user_id)
        # In production, you would store this in database with encryption for API keys
        user_model_configs[user.id] = {
            "model_provider": config.model_provider,
            "api_key": config.api_key,  # In production: encrypt this!
            "model_name": config.model_name,
            "updated_at": datetime.now()
        }
        
        # Log configuration update
        print(f"✅ User {user.username} (ID: {user.id}) configured model:")
        print(f"   Provider: {config.model_provider}")
        print(f"   Model: {config.model_name or 'default'}")
        
        # Prepare response message
        message = f"Model configuration saved successfully for {config.model_provider}"
        if config.model_name:
            message += f" using {config.model_name}"
        
        return ModelConfigResponse(
            success=True,
            message=message,
            provider=config.model_provider,
            model_name=config.model_name
        )
    
    except Exception as e:
        print(f"❌ Error configuring model for user {user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save model configuration: {str(e)}"
        )


@app.get("/config/model", response_model=dict)
async def get_model_config(
    user: User = Depends(get_current_user)
):
    """
    Get current model configuration for the user
    """
    config = user_model_configs.get(user.id)
    
    if not config:
        return {
            "configured": False,
            "message": "No model configuration found. Using default settings."
        }
    
    # Don't send the API key back (security)
    return {
        "configured": True,
        "model_provider": config["model_provider"],
        "model_name": config.get("model_name"),
        "updated_at": config["updated_at"].isoformat(),
        "has_api_key": bool(config.get("api_key"))
    }


# ==================== Conversation Endpoints ====================

@app.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conv_data: ConversationCreate,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """Create a new conversation for the current user"""
    user = await get_current_user(credentials, db)
    
    new_conv = Conversation(
        user_id=user.id,
        title=conv_data.title or "New Chat"
    )
    
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    
    return ConversationResponse(
        id=new_conv.id,
        title=new_conv.title,
        created_at=new_conv.created_at.isoformat(),
        updated_at=new_conv.updated_at.isoformat(),
        message_count=0
    )


@app.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user"""
    user = await get_current_user(credentials, db)
    
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user.id,
        Conversation.is_active == True
    ).order_by(Conversation.updated_at.desc()).all()
    
    result = []
    for conv in conversations:
        msg_count = db.query(ChatMessage).filter(ChatMessage.conversation_id == conv.id).count()
        result.append(ConversationResponse(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat(),
            message_count=msg_count
        ))
    
    return result


@app.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: int,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages"""
    user = await get_current_user(credentials, db)
    
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id
    ).first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id
    ).order_by(ChatMessage.timestamp.asc()).all()
    
    msg_responses = []
    for msg in messages:
        sources = json.loads(msg.sources) if msg.sources else None
        confidence = json.loads(msg.confidence) if msg.confidence else None
        msg_responses.append(ChatMessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            sources=sources,
            confidence=confidence,
            timestamp=msg.timestamp.isoformat()
        ))
    
    return ConversationDetailResponse(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        messages=msg_responses
    )


@app.put("/conversations/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: int,
    title_data: ConversationUpdateTitle,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """Update conversation title"""
    user = await get_current_user(credentials, db)
    
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id
    ).first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conv.title = title_data.title
    db.commit()
    
    return {"message": "Title updated successfully", "title": conv.title}


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """Delete a conversation (soft delete)"""
    user = await get_current_user(credentials, db)
    
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id
    ).first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conv.is_active = False
    db.commit()
    
    return {"message": "Conversation deleted successfully"}


@app.post("/conversations/{conversation_id}/messages", response_model=ChatMessageResponse)
async def add_message_to_conversation(
    conversation_id: int,
    message: ChatMessageCreate,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """Add a message to a conversation"""
    user = await get_current_user(credentials, db)
    
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id
    ).first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Create message
    new_msg = ChatMessage(
        conversation_id=conversation_id,
        role=message.role,
        content=message.content,
        sources=json.dumps(message.sources) if message.sources else None,
        confidence=json.dumps(message.confidence) if message.confidence else None
    )
    
    db.add(new_msg)
    
    # Update conversation title from first user message if it's still "New Chat"
    if conv.title == "New Chat" and message.role == "user":
        # Use first 50 chars of message as title
        conv.title = message.content[:50] + ("..." if len(message.content) > 50 else "")
    
    db.commit()
    db.refresh(new_msg)
    
    return ChatMessageResponse(
        id=new_msg.id,
        role=new_msg.role,
        content=new_msg.content,
        sources=message.sources,
        confidence=message.confidence,
        timestamp=new_msg.timestamp.isoformat()
    )


# ==================== Helper Functions ====================

def generate_answer_from_context(query: str, documents: List[str], metadatas: List[dict]) -> str:
    """
    Simple answer generation from context (simulated LLM)
    In production, this would call OpenAI GPT-4 or similar
    """
    # For demonstration, create a simple extractive answer
    if not documents:
        return "I don't have access to relevant information to answer your question."
    
    # Combine top documents
    combined_context = "\n\n".join(documents[:3])  # Use top 3 documents
    
    # Extract departments from metadata
    departments = set(meta.get('department', 'Unknown') for meta in metadatas)
    
    # Create answer with source attribution
    answer = f"Based on the available information from {', '.join(departments)} department(s):\n\n"
    
    # Add relevant excerpts
    for i, doc in enumerate(documents[:2], 1):
        # Take first 300 characters as excerpt
        excerpt = doc[:300].strip()
        if len(doc) > 300:
            excerpt += "..."
        answer += f"{excerpt}\n\n"
    
    answer += f"\n(Answer compiled from {len(documents)} relevant source(s))"
    
    return answer


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
