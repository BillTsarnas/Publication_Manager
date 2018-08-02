from flask import Flask

app = Flask(__name__)
app._static_folder= "templates/static"


from comp62521 import views
