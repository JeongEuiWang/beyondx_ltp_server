import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from app.core.config import settings
from fastapi import HTTPException


class EmailSender:
    def __init__(
        self,
        subject: str,
        receiver_email: str,
        client_name: str,
        order_primary: str,
        quote_id: str,
    ):
        self.SMTP_HOST = settings.SMTP_HOST
        self.SMTP_PORT = settings.SMTP_PORT
        self.SMTP_EMAIL_USERNAME = settings.SMTP_EMAIL_USERNAME
        self.SMTP_EMAIL_PASSWORD = settings.SMTP_EMAIL_PASSWORD
        self.subject = subject
        self.receiver_email = receiver_email
        self.client_name = client_name
        self.sender_email = settings.SMTP_SENDER_EMAIL
        self.order_primary = order_primary
        self.quote_id = quote_id
        if not all(
            [
                self.SMTP_HOST,
                self.SMTP_EMAIL_USERNAME,
                self.SMTP_EMAIL_PASSWORD,
                self.sender_email,
            ]
        ):
            missing_configs = []
            if not self.SMTP_HOST:
                missing_configs.append("SMTP_HOST")
            if not self.SMTP_EMAIL_USERNAME:
                missing_configs.append("SMTP_EMAIL_USERNAME")
            if not self.SMTP_EMAIL_PASSWORD:
                missing_configs.append("SMTP_EMAIL_PASSWORD")
            if not self.sender_email:
                missing_configs.append("SMTP_SENDER_EMAIL or SMTP_EMAIL_USERNAME")
            raise ValueError(
                f"SMTP 설정이 환경 변수에 누락되었습니다: {', '.join(missing_configs)}"
            )

    def _format_body_as_html(self) -> str:
        body_template = f"""
<h1>Hello {self.client_name}</h1>
<br/>
<br/>

<p>Your order has been received for Load #{self.order_primary}</p>
<br/>
<p>Once it is accepted, a BOL will be emailed from {self.sender_email}</p>
<br/>

<p>This is not final cost, however, it can be updated depending on time, condition of freight, or additional requests from customer,
We will try our best to contact you before making any decisions of additional cost
<br/>
For any questions or concerns regarding this order, contact <a href="mailto:dispatch@beyondxus.com" style="color: #0066cc; text-decoration: underline;">dispatch@beyondxus.com</a>.</p>

<br/>
<p>You can check your order status by clicking the link below. When your order is approved, it will show ACCEPT status.</p>
<p><a href="http://localhost:5173/service" style="color: #0066cc; text-decoration: underline;">Check Your Order Status</a></p>
<br/>

<p>==================================================</p>
        """
        return body_template.format()

    async def send_email(self) -> None:
        """
        구성된 정보로 이메일을 발송합니다.
        성공 시 True, 실패 시 False를 반환합니다.
        """
        if not self.sender_email:
            raise HTTPException(
                status_code=500,
                detail="오류: 발신자 이메일이 설정되지 않았습니다. SMTP_SENDER_EMAIL_NEW 또는 SMTP_EMAIL_USERNAME_NEW 환경 변수를 확인하세요.",
            )

        msg = MIMEMultipart()
        msg["Subject"] = self.subject
        msg["From"] = self.sender_email
        msg["To"] = self.receiver_email

        html_part = MIMEText(self._format_body_as_html(), "html", "utf-8")
        msg.attach(html_part)



        try:
            print(f"SMTP 서버에 연결 중: {self.SMTP_HOST}:{self.SMTP_PORT}")
            with smtplib.SMTP(
                self.SMTP_HOST, self.SMTP_PORT, timeout=10
            ) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                print(f"로그인 시도: {self.SMTP_EMAIL_USERNAME}")
                server.login(self.SMTP_EMAIL_USERNAME, self.SMTP_EMAIL_PASSWORD)
                print(
                    f"이메일 발송 중: 받는 사람 <{self.receiver_email}>, 발신자 <{self.sender_email}>"
                )
                server.sendmail(self.sender_email, self.receiver_email, msg.as_string())
                print("이메일이 성공적으로 발송되었습니다!")
        except smtplib.SMTPAuthenticationError as e:
            print(
                f"SMTP 인증 오류: {e}. 사용자 이름/비밀번호 및 서버 설정을 확인하세요."
            )
            raise HTTPException(status_code=500, detail=str(e))
        except smtplib.SMTPConnectError as e:
            print(f"SMTP 연결 오류: {e}. SMTP 호스트 및 포트를 확인하세요.")
            raise HTTPException(status_code=500, detail=str(e))
        except smtplib.SMTPServerDisconnected as e:
            print(f"SMTP 서버 연결 끊김: {e}.")
            raise HTTPException(status_code=500, detail=str(e))
        except smtplib.SMTPException as e:
            print(f"SMTP 관련 오류 발생: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        except ConnectionRefusedError as e:
            print(
                f"연결 거부됨: {e}. SMTP 서버가 해당 포트에서 실행 중인지 확인하세요."
            )
            raise HTTPException(status_code=500, detail=str(e))
        except TimeoutError as e:
            print(
                f"연결 시간 초과: {e}. 네트워크 연결 또는 SMTP 서버 응답을 확인하세요."
            )
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            print(f"이메일 발송 중 예기치 않은 오류 발생: {e}")
            raise HTTPException(status_code=500, detail=str(e))
