"""Explicit AUTH-008 bindings; the production migrator is the system under test."""

from pytest_bdd import scenario


@scenario('AUTH-008-database-migration.feature', '全量遷移保留全部應用資料及原有欄位值')
def test_all_data() -> None:
    """AUTH-008 acceptance scenario."""


@scenario('AUTH-008-database-migration.feature', '遷移後既有會員可用原密碼登入')
def test_original_password() -> None:
    """AUTH-008 acceptance scenario."""


@scenario('AUTH-008-database-migration.feature', '遷移保留失敗次數且下一次錯誤仍觸發原鎖定規則')
def test_retained_failures() -> None:
    """AUTH-008 acceptance scenario."""


@scenario('AUTH-008-database-migration.feature', '遷移不提前解除鎖定也不延長原鎖定期限')
def test_original_lock_deadline() -> None:
    """AUTH-008 acceptance scenario."""


@scenario('AUTH-008-database-migration.feature', '遷移後原瀏覽器可沿用尚未到期的 Session')
def test_original_session() -> None:
    """AUTH-008 acceptance scenario."""


@scenario('AUTH-008-database-migration.feature', '已過期的 Session 遷移後不會恢復有效登入')
def test_expired_session() -> None:
    """AUTH-008 acceptance scenario."""


@scenario('AUTH-008-database-migration.feature', '目標存在同名會員時不直接覆寫原有資料')
def test_target_conflict() -> None:
    """AUTH-008 acceptance scenario."""
