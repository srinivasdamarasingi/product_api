from sqlalchemy import text


def test_transaction_example(db_session):

    result = db_session.execute(
        text("SELECT 1")
    )

    assert result.scalar() == 1