import pytest

from semantic_search.semantic_search import is_authorized

# --------------------------------------------------
# Sample document metadata (used across tests)
# --------------------------------------------------

PUBLIC_DOC = {
    "department": "General",
    "classification": "public",
    "permitted_roles": ""
}

INTERNAL_DOC = {
    "department": "General",
    "classification": "internal",
    "permitted_roles": "Employees"
}

CONFIDENTIAL_DOC = {
    "department": "General",
    "classification": "confidential",
    "permitted_roles": "Employees, C-Level Executive"
}

RESTRICTED_DOC = {
    "department": "Finance",
    "classification": "restricted",
    "permitted_roles": "C-Level Executive"
}

ENGINEERING_DOC = {
    "department": "Engineering",
    "classification": "internal",
    "permitted_roles": "Engineering Employee, Engineering Manager"
}


# --------------------------------------------------
# INTERN TESTS
# --------------------------------------------------

def test_intern_can_read_public():
    assert is_authorized("intern", PUBLIC_DOC) is True


def test_intern_cannot_read_internal():
    assert is_authorized("intern", INTERNAL_DOC) is False


def test_intern_cannot_read_confidential():
    assert is_authorized("intern", CONFIDENTIAL_DOC) is False


# --------------------------------------------------
# EMPLOYEE TESTS
# --------------------------------------------------

def test_employee_can_read_internal():
    assert is_authorized("employee", INTERNAL_DOC) is True


def test_employee_cannot_read_confidential():
    assert is_authorized("employee", CONFIDENTIAL_DOC) is False


# --------------------------------------------------
# MANAGER / HR TESTS
# --------------------------------------------------

def test_hr_manager_can_read_confidential_hr_doc():
    hr_confidential = {
        "department": "HR",
        "classification": "confidential",
        "permitted_roles": "HR Manager"
    }
    assert is_authorized("HR Manager", hr_confidential) is True


# --------------------------------------------------
# C-LEVEL TESTS
# --------------------------------------------------

def test_c_level_can_read_confidential():
    assert is_authorized("C-Level Executive", CONFIDENTIAL_DOC) is True


def test_c_level_can_read_restricted():
    assert is_authorized("CTO", RESTRICTED_DOC) is True


# --------------------------------------------------
# ADMIN TESTS
# --------------------------------------------------

def test_admin_can_read_everything():
    assert is_authorized("admin", RESTRICTED_DOC) is True

# --------------------------------------------------
# ENGINEERING RBAC TESTS
# --------------------------------------------------

def test_engineering_employee_can_read_engineering_doc():
    assert is_authorized("Backend Developer", ENGINEERING_DOC) is True


def test_engineering_manager_can_read_engineering_doc():
    assert is_authorized("Engineering Lead", ENGINEERING_DOC) is True


def test_employee_cannot_read_engineering_doc():
    assert is_authorized("employee", ENGINEERING_DOC) is False


def test_intern_cannot_read_engineering_doc():
    assert is_authorized("intern", ENGINEERING_DOC) is False
