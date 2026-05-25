from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings

_conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_USER,
    MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

_mail = FastMail(_conf)


async def send_verification_code(to_email: str, code: str) -> None:
    html = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: auto; padding: 24px; text-align: center;">
      <h2 style="color: #333;">이메일 인증 코드</h2>
      <p>안녕하세요, 익명 매칭 서비스에 가입해주셔서 감사합니다.</p>
      <p>아래 6자리 코드를 인증 화면에 입력해주세요.</p>
      <div style="font-size: 36px; font-weight: bold; letter-spacing: 8px;
                  color: #4F46E5; margin: 32px 0; padding: 16px;
                  background: #F3F4F6; border-radius: 8px;">
        {code}
      </div>
      <p style="font-size: 12px; color: #777;">
        이 코드는 {settings.EMAIL_CODE_EXPIRE_MINUTES}분 동안 유효합니다.<br>
        본인이 요청하지 않았다면 이 메일을 무시해주세요.
      </p>
    </div>
    """

    message = MessageSchema(
        subject="[익명 매칭] 이메일 인증 코드",
        recipients=[to_email],
        body=html,
        subtype=MessageType.html,
    )
    await _mail.send_message(message)


async def send_password_reset_code(to_email: str, code: str) -> None:
    html = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: auto; padding: 24px; text-align: center;">
      <h2 style="color: #333;">비밀번호 재설정 코드</h2>
      <p>비밀번호 재설정을 요청하셨습니다.</p>
      <p>아래 6자리 코드를 입력해주세요.</p>
      <div style="font-size: 36px; font-weight: bold; letter-spacing: 8px;
                  color: #DC2626; margin: 32px 0; padding: 16px;
                  background: #FEF2F2; border-radius: 8px;">
        {code}
      </div>
      <p style="font-size: 12px; color: #777;">
        이 코드는 {settings.EMAIL_CODE_EXPIRE_MINUTES}분 동안 유효합니다.<br>
        본인이 요청하지 않았다면 즉시 비밀번호를 변경해주세요.
      </p>
    </div>
    """

    message = MessageSchema(
        subject="[익명 매칭] 비밀번호 재설정 코드",
        recipients=[to_email],
        body=html,
        subtype=MessageType.html,
    )
    await _mail.send_message(message)