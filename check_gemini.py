import tomllib
from pathlib import Path

from google import genai
from google.genai import errors


# Connect to Gemini API using credentials from a TOML file & to Streamlit.

secrets_path = (Path(__file__).resolve().parent / ".streamlit" / "secrets.toml")

try:
    with secrets_path.open("rb") as secrets_file:
        secrets = tomllib.load(secrets_file)

    client = genai.Client(api_key=secrets["GEMINI_API_KEY"])

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=(
                "You are the digital barista for One Stop Coffee. "
                "Write one short sentence welcoming a customer. "
                "Do not mention products or prices."
            ),
        )

        if response.text:
            print("Gemini reply:")
            print(response.text)
        else:
            print("Google returned no text.")

    finally:
        client.close()
        
except FileNotFoundError:
    print(f"Oops..file not found .streamlit/secrets.toml.Please create a file")
    
except KeyError:
        print(f"Oops..GEMINI_API_KEY not found in .streamlit/secrets.toml. Please add your API key.")
        
        
except tomllib.TOMLDecodeError:
    print(f"Oops..Invalid TOML format in .streamlit/secrets.toml. Please check the file.")
    
except errors.APIError as error:
    message = str(error.message).replace(
        secrets["GEMINI_API_KEY"], "[HIDDEN]"
    )
    print(f"Google error {error.code}: {message}")
    
    
except Exception as error:
    print(f"Connection check failed: {type(error).__name__}")
