
from .model_init import db
from sqlalchemy.orm import relationship

if db is None:
    raise Exception("Database not initialized. Please call init_db(db) before importing models")


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    mail = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(256), nullable=False, unique=True)
    derivedKeySalt = db.Column(db.String(256), nullable=False)
    isVerified = db.Column(db.Boolean, nullable=False)
    passphraseSalt = db.Column(db.String(256), nullable=False)
    createdAt = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(256), nullable=False, default="user")
    isBlocked =  db.Column(db.Boolean, nullable=False, default=False)
    last_login_date = db.Column(db.String(20), nullable=True)

    zke_encryption_key = relationship("ZKE_encryption_key", cascade="all, delete-orphan", back_populates="user", passive_deletes=True)
    totp_secrets = relationship("TOTP_secret", cascade="all, delete-orphan" , back_populates="user")
    oauth_tokens = relationship("Oauth_tokens", cascade="all, delete-orphan", back_populates="user")
    google_drive_integration = relationship("GoogleDriveIntegration", cascade="all, delete-orphan", back_populates="user")
    preferences = relationship("Preferences", cascade="all, delete-orphan", back_populates="user")
    email_verification_token = relationship("EmailVerificationToken", cascade="all, delete-orphan", back_populates="user")
    rate_limiting = relationship("RateLimiting", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", cascade="all, delete-orphan", back_populates="user")
    session_tokens = relationship("SessionToken", cascade="all, delete-orphan", back_populates="user")
    sessions = relationship("Session", cascade="all, delete-orphan", back_populates="user")
    backup_configuration = relationship("BackupConfiguration", cascade="all, delete-orphan", back_populates="user")



class ZKE_encryption_key(db.Model):
    __tablename__ = "ZKE_encryption_key"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id", name="fk_zke_encryption_key_user_id", ondelete="CASCADE"), nullable=False)
    ZKE_key = db.Column(db.String(256), nullable=False)

    user = relationship("User", back_populates="zke_encryption_key")

class TOTP_secret(db.Model):
    __tablename__ = "totp_secret_enc"
    uuid = db.Column(db.String(256), primary_key=True, nullable=False, autoincrement=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id", name="fk_totp_secret_user_id"), nullable=False)
    secret_enc = db.Column(db.Text, nullable=False)

    user = relationship("User", back_populates="totp_secrets")


class Oauth_tokens(db.Model):
    __tablename__ = "oauth_tokens"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id", name="fk_oauth_tokens_user_id"), nullable=False)
    enc_credentials = db.Column(db.Text, nullable=False)
    cipher_nonce = db.Column(db.Text, nullable=False)
    cipher_tag = db.Column(db.Text, nullable=False)
    expires_at = db.Column(db.Integer, nullable=False)

    user = relationship("User", back_populates="oauth_tokens")

class GoogleDriveIntegration(db.Model):
    __tablename__ = "google_drive_integration"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id",  name="fk_google_drive_integration_user_id"), nullable=False)
    isEnabled = db.Column(db.Boolean, nullable=False, default=False)
    lastBackupCleanDate = db.Column(db.String(256), nullable=True, default=None)

    user = relationship("User", back_populates="google_drive_integration")


class Preferences(db.Model):
    __tablename__ = "preferences"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id", name="fk_preferences_user_id"), nullable=False)
    favicon_preview_policy = db.Column(db.String(256), nullable=True, default="enabledOnly")
    derivation_iteration = db.Column(db.Integer, nullable=True, default=700000)
    minimum_backup_kept = db.Column(db.Integer, nullable=True, default=20)
    backup_lifetime = db.Column(db.Integer, nullable=True, default=30)
    vault_autolock_delay_min = db.Column(db.Integer, nullable=True, default=10)

    user = relationship("User", back_populates="preferences")

class EmailVerificationToken(db.Model):
    __tablename__ = "email_verification_token"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id", name="fk_email_verification_token_user_id"), nullable=False, unique=True)
    token = db.Column(db.String(256), nullable=False)
    expiration = db.Column(db.String(256), nullable=False)
    failed_attempts = db.Column(db.Integer, nullable=False, default=0)

    user = relationship("User", back_populates="email_verification_token")

class RateLimiting(db.Model):
    __tablename__ = "rate_limiting"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    ip = db.Column(db.String(45), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id", name="fk_rate_limiting_user_id"), nullable=True)
    action_type = db.Column(db.String(256), nullable=False) # send_verification_email, failed_login 
    timestamp = db.Column(db.DateTime, nullable=False)
    
class Notifications(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.String(36), primary_key=True, nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.String(20), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    expiry = db.Column(db.String(20), nullable=True, default=None)
    authenticated_user_only =  db.Column(db.Boolean, nullable=False, default=False)


class RefreshToken(db.Model):
    __tablename__ = "refresh_token"
    id = db.Column(db.String(36), primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id", name="fk_refresh_token_user_id"), nullable=False)
    hashed_token = db.Column(db.String(64), nullable=False, unique=True)
    expiration = db.Column(db.String(20), nullable=False)
    session_token_id = db.Column(db.String(36), nullable=False)
    revoke_timestamp = db.Column(db.String(20), nullable=True, default=None)

    session_id = db.Column(db.String(36), db.ForeignKey("session.id", name="fk_refresh_token_session_id"), nullable=False)
    session = relationship("Session", back_populates="refresh_tokens")
    user = relationship("User", back_populates="refresh_tokens")

class SessionToken(db.Model):
    __tablename__ = "session_token"
    id = db.Column(db.String(36), primary_key=True, nullable=False)
    token = db.Column(db.String(36), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id", name="fk_session_token_user_id"), nullable=False)
    expiration = db.Column(db.String(20), nullable=False)
    revoke_timestamp = db.Column(db.String(20), nullable=True, default=None)

    # Relationship to Session
    session_id = db.Column(db.String(36), db.ForeignKey("session.id", name="fk_session_token_session_id"), nullable=False)
    session = relationship("Session", back_populates="session_tokens")

    user = relationship("User", back_populates="session_tokens")


class Session(db.Model):
    __tablename__ = "session"
    id = db.Column(db.String(36), primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id", name="fk_session_user_id"), nullable=False)

    # Metadata about the session is encrypted by the user.
    encrypted_user_agent = db.Column(db.String(512), nullable=True)
    encrypted_device_name = db.Column(db.String(256), nullable=True)
    encrypted_platform = db.Column(db.String(256), nullable=True)

    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.String(20), nullable=False)
    last_active_at = db.Column(db.String(20), nullable=False)
    expiration_timestamp = db.Column(db.String(20), nullable=False)
    revoke_timestamp = db.Column(db.String(20), nullable=True, default=None)

    refresh_tokens = relationship("RefreshToken", back_populates="session", cascade="all, delete-orphan")
    session_tokens = relationship("SessionToken", back_populates="session", cascade="all, delete-orphan")

    user = relationship("User", back_populates="sessions")



class BackupConfiguration(db.Model):
    __tablename__ = "backup_configuration"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id", name="fk_backup_configuration_user_id"), nullable=False)
    backup_max_age_days = db.Column(db.Integer, nullable=False, default=30)
    backup_minimum_count = db.Column(db.Integer, nullable=False, default=20)

    user = relationship("User", back_populates="backup_configuration")