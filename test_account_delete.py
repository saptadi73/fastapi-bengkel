import uuid
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.accounting import Account, JournalLine
from services.services_accounting import AccountDeletionConflictError, delete_account


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Account.__table__.create(engine)
    JournalLine.__table__.create(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def add_account(db, code, account_type="asset"):
    account = Account(
        id=uuid.uuid4(),
        code=code,
        name=f"Account {code}",
        normal_balance="debit",
        account_type=account_type,
        is_active=True,
    )
    db.add(account)
    db.commit()
    return account


def test_delete_account_when_same_type_and_prefix_remains(db):
    account = add_account(db, "1001")
    remaining_account = add_account(db, "1002")

    deleted = delete_account(db, str(account.id))

    assert deleted["code"] == "1001"
    assert db.query(Account).filter(Account.id == account.id).first() is None
    assert db.query(Account).filter(Account.id == remaining_account.id).first() is not None


def test_delete_account_rejects_last_same_type_and_prefix(db):
    account = add_account(db, "1200", "asset")
    add_account(db, "1201", "liability")

    with pytest.raises(AccountDeletionConflictError, match="Account terakhir"):
        delete_account(db, str(account.id))

    assert db.query(Account).filter(Account.id == account.id).first() is not None


def test_delete_account_rejects_account_used_in_journal(db):
    account = add_account(db, "1001")
    add_account(db, "1002")
    db.add(
        JournalLine(
            id=uuid.uuid4(),
            entry_id=uuid.uuid4(),
            account_id=account.id,
            description="Used account",
            debit=Decimal("1.00"),
            credit=Decimal("0.00"),
        )
    )
    db.commit()

    with pytest.raises(AccountDeletionConflictError, match="digunakan dalam jurnal"):
        delete_account(db, str(account.id))

    assert db.query(Account).filter(Account.id == account.id).first() is not None
