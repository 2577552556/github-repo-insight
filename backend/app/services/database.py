"""
Analysis Workspace - SQLite Database Service

使用 SQLite 持久化分析记录和凭据。
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import Column, String, Integer, Text, DateTime, create_engine, Index
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

Base = declarative_base()


class AnalysisRecordModel(Base):
    """分析记录数据库模型"""
    __tablename__ = "analysis_records"

    id = Column(String(36), primary_key=True)
    repository_url = Column(String(500), nullable=False)
    repository_name = Column(String(255), nullable=False)
    owner = Column(String(255), nullable=False)
    full_name = Column(String(500), nullable=False)

    # 评分摘要
    score = Column(Integer, nullable=True)
    grade = Column(String(1), nullable=True)
    type_detection = Column(Text, nullable=True)  # JSON

    # 状态
    status = Column(String(20), nullable=False, default="processing")
    error_message = Column(Text, nullable=True)

    # 版本和时间
    analysis_version = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 完整结果
    result_json = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_repository_name", "repository_name"),
        Index("idx_created_at", "created_at"),
    )


class CredentialModel(Base):
    """凭据数据库模型（加密存储）"""
    __tablename__ = "credentials"

    id = Column(String(36), primary_key=True)
    provider = Column(String(50), nullable=False)  # 'github', 'deepseek', 'openai'
    name = Column(String(50), nullable=False)  # 'token', 'api_key'
    encrypted_value = Column(Text, nullable=False)  # AES 加密后的密文
    iv = Column(String(50), nullable=False)  # 初始化向量
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_provider_name", "provider", "name"),
    )


class DatabaseService:
    """SQLite 数据库服务"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "analysis.db"
        self.db_path = str(db_path)

        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        # 创建表
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()

    def create_analysis_record(
        self,
        repository_url: str,
        repository_name: str,
        owner: str,
        full_name: str,
    ) -> str:
        """创建新的分析记录，返回 ID"""
        record_id = str(uuid.uuid4())

        session = self.get_session()
        try:
            record = AnalysisRecordModel(
                id=record_id,
                repository_url=repository_url,
                repository_name=repository_name,
                owner=owner,
                full_name=full_name,
                status="processing",
            )
            session.add(record)
            session.commit()
            return record_id
        finally:
            session.close()

    def update_analysis_record(
        self,
        record_id: str,
        status: Optional[str] = None,
        score: Optional[int] = None,
        grade: Optional[str] = None,
        type_detection: Optional[dict] = None,
        error_message: Optional[str] = None,
        result_json: Optional[dict] = None,
    ) -> bool:
        """更新分析记录"""
        session = self.get_session()
        try:
            record = session.query(AnalysisRecordModel).filter(
                AnalysisRecordModel.id == record_id
            ).first()

            if not record:
                return False

            if status is not None:
                record.status = status
            if score is not None:
                record.score = score
            if grade is not None:
                record.grade = grade
            if type_detection is not None:
                record.type_detection = json.dumps(type_detection, ensure_ascii=False)
            if error_message is not None:
                record.error_message = error_message
            if result_json is not None:
                record.result_json = json.dumps(result_json, ensure_ascii=False)

            record.updated_at = datetime.now(timezone.utc)

            session.commit()
            return True
        finally:
            session.close()

    def get_analysis_record(self, record_id: str) -> Optional[dict]:
        """获取单条分析记录"""
        session = self.get_session()
        try:
            record = session.query(AnalysisRecordModel).filter(
                AnalysisRecordModel.id == record_id
            ).first()

            if not record:
                return None

            return self._record_to_dict(record)
        finally:
            session.close()

    def get_analysis_history(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> list[dict]:
        """获取分析历史记录列表"""
        session = self.get_session()
        try:
            query = session.query(AnalysisRecordModel)

            if search:
                query = query.filter(
                    AnalysisRecordModel.repository_name.ilike(f"%{search}%")
                )

            records = (
                query.order_by(AnalysisRecordModel.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )

            return [self._record_to_dict(r) for r in records]
        finally:
            session.close()

    def delete_analysis_record(self, record_id: str) -> bool:
        """删除分析记录"""
        session = self.get_session()
        try:
            record = session.query(AnalysisRecordModel).filter(
                AnalysisRecordModel.id == record_id
            ).first()

            if not record:
                return False

            session.delete(record)
            session.commit()
            return True
        finally:
            session.close()

    # ========== Credentials CRUD ==========

    def save_credential(
        self,
        provider: str,
        name: str,
        encrypted_value: str,
        iv: str,
    ) -> str:
        """保存或更新凭据，返回 ID"""
        session = self.get_session()
        try:
            # 检查是否已存在
            existing = session.query(CredentialModel).filter(
                CredentialModel.provider == provider,
                CredentialModel.name == name,
            ).first()

            if existing:
                existing.encrypted_value = encrypted_value
                existing.iv = iv
                existing.updated_at = datetime.now(timezone.utc)
                session.commit()
                return existing.id
            else:
                cred_id = str(uuid.uuid4())
                cred = CredentialModel(
                    id=cred_id,
                    provider=provider,
                    name=name,
                    encrypted_value=encrypted_value,
                    iv=iv,
                )
                session.add(cred)
                session.commit()
                return cred_id
        finally:
            session.close()

    def get_credential(self, provider: str, name: str) -> Optional[dict]:
        """获取凭据（返回加密后的密文和 IV）"""
        session = self.get_session()
        try:
            cred = session.query(CredentialModel).filter(
                CredentialModel.provider == provider,
                CredentialModel.name == name,
            ).first()

            if not cred:
                return None

            return {
                "id": cred.id,
                "provider": cred.provider,
                "name": cred.name,
                "encrypted_value": cred.encrypted_value,
                "iv": cred.iv,
                "created_at": cred.created_at.isoformat() if cred.created_at else None,
                "updated_at": cred.updated_at.isoformat() if cred.updated_at else None,
            }
        finally:
            session.close()

    def delete_credential(self, provider: str, name: str) -> bool:
        """删除凭据"""
        session = self.get_session()
        try:
            cred = session.query(CredentialModel).filter(
                CredentialModel.provider == provider,
                CredentialModel.name == name,
            ).first()

            if not cred:
                return False

            session.delete(cred)
            session.commit()
            return True
        finally:
            session.close()

    def list_credentials(self, provider: str) -> list[dict]:
        """列出某 provider 下所有凭据（不返回密文）"""
        session = self.get_session()
        try:
            creds = session.query(CredentialModel).filter(
                CredentialModel.provider == provider
            ).all()

            return [
                {
                    "id": c.id,
                    "provider": c.provider,
                    "name": c.name,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                }
                for c in creds
            ]
        finally:
            session.close()

    def _record_to_dict(self, record: AnalysisRecordModel) -> dict:
        """将记录转换为字典"""
        result = {
            "id": record.id,
            "repository_url": record.repository_url,
            "repository_name": record.repository_name,
            "owner": record.owner,
            "full_name": record.full_name,
            "score": record.score,
            "grade": record.grade,
            "type_detection": (
                json.loads(record.type_detection)
                if record.type_detection
                else None
            ),
            "status": record.status,
            "error_message": record.error_message,
            "analysis_version": record.analysis_version,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        }

        if record.result_json:
            result["result_json"] = json.loads(record.result_json)

        return result


# 全局实例
db_service = DatabaseService()