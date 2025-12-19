from app import create_app

app = create_app()
app.config['testMode'] = True
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)