ROLE_ACCESS = {
    "Employee": ["employee_handbook"],
    "HR": ["hr_data"],
    "Engineering": ["engineering_docs"],
    "Finance": ["quarterly_financial_report"],
    "Marketing": ["marketing_report"],
    "C-Level": ["employee_handbook", "hr_data", "engineering_docs",
                "quarterly_financial_report", "marketing_report"],
}


def is_allowed(user_role, doc_role):
    return doc_role in ROLE_ACCESS.get(user_role, [])
