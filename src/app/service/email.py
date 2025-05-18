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
        client_id: str,
        quote: str,
        pdf_buffer: bytes,
        pdf_filename: str = "bol.pdf",
    ):
        self.SMTP_HOST = settings.SMTP_HOST
        self.SMTP_PORT = settings.SMTP_PORT  # 기본 포트 587 (TLS)
        self.SMTP_EMAIL_USERNAME = settings.SMTP_EMAIL_USERNAME
        self.SMTP_EMAIL_PASSWORD = settings.SMTP_EMAIL_PASSWORD
        self.subject = subject
        self.receiver_email = receiver_email
        self.client_id = client_id
        self.quote = quote
        self.pdf_buffer = pdf_buffer
        self.pdf_filename = pdf_filename  # 첨부될 PDF 파일의 이름
        self.sender_email = settings.SMTP_SENDER_EMAIL

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
        # f-string 내에서 중괄호를 문자 그대로 사용하려면 {{ }} 와 같이 두 번 사용합니다.
        # 이후 .format() 메서드로 실제 값을 삽입합니다.
        body_template = f"""
<h1>Dear Valued customer,</h1>
<br/>
<br/>

<p>Your order AAA has been created and notified our dispatch team,
<br/>
Will follow up on this order and contact you if we need any further information.</p>

<p>Please be informed that your quoted rate for this order is USD.<br>
This is not final cost, however, it can be updated depending on time, condition of freight, or additional requests from customer,<br>
We will try our best to contact you before making any decisions of additional cost.</p>

<p>If you need a further assistance, please contact us via email:</p>

<p>Operations : dispatch@beyondxus.com<br>
Accounting : acct@beyondxus.com<br>
Others : all@beyondxus.com</p>

<p>==================================================</p>

<p>The methods of payment are as follows:</p>

<p>Zelle: all@beyondxus.com<br>
Bank:<br>
Bank Name: Chase Bank<br>
Account Name: Beyond X LLC<br>
Routing Number: 111000614 (Direct Deposit/ACH) / 021000021 (Wire Transfer)<br>
Account Number: 500099497<br>
SWIFT/BIC:<br>
Check: Please make the check payable to 'Beyond X LLC' and mail it to<br>
1431 Greenway Dr., Suite 400, Irving TX 75038</p>

<p>==================================================</p>
        """
        # TODO: quote Id and total price
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

        # HTML 본문 추가
        html_part = MIMEText(self._format_body_as_html(), "html", "utf-8")
        msg.attach(html_part)

        # PDF 첨부파일 추가
        if self.pdf_buffer and self.pdf_filename:
            part = MIMEApplication(self.pdf_buffer, Name=self.pdf_filename)
            part["Content-Disposition"] = f'attachment; filename="{self.pdf_filename}"'
            msg.attach(part)
            print(f"첨부파일 준비: '{self.pdf_filename}'")
        else:
            print(
                "경고: PDF 버퍼 또는 파일 이름이 제공되지 않아 첨부파일 없이 발송될 수 있습니다."
            )
            # 필요시 여기서 오류를 발생시키거나 로직을 조정할 수 있습니다.

        try:
            print(f"SMTP 서버에 연결 중: {self.SMTP_HOST}:{self.SMTP_PORT}")
            # `with` 문을 사용하여 smtplib.SMTP 객체가 자동으로 닫히도록 합니다.
            with smtplib.SMTP(
                self.SMTP_HOST, self.SMTP_PORT, timeout=10
            ) as server:  # 타임아웃 설정
                server.ehlo()  # 확장 SMTP 서버에 자신을 식별
                server.starttls()  # TLS 암호화 시작
                server.ehlo()  # TLS 핸드셰이크 후 다시 ehlo
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
        except ConnectionRefusedError as e:  # 소켓 레벨 오류
            print(
                f"연결 거부됨: {e}. SMTP 서버가 해당 포트에서 실행 중인지 확인하세요."
            )
            raise HTTPException(status_code=500, detail=str(e))
        except TimeoutError as e:  # 소켓 레벨 타임아웃
            print(
                f"연결 시간 초과: {e}. 네트워크 연결 또는 SMTP 서버 응답을 확인하세요."
            )
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            print(f"이메일 발송 중 예기치 않은 오류 발생: {e}")
            raise HTTPException(status_code=500, detail=str(e))
