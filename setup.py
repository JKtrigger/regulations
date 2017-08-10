from distutils.core import setup
import py2exe
setup(
    data_files=[(".", ["mail_sender.conf.scel"])],
    console=["application.py"],
    options={
        "py2exe": {
            "includes": [
                "email.mime.multipart", "email.mime.text", "email.mime.base"
            ]
        }
    }
)
