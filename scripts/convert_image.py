import base64
import os

img_path = r"C:\Users\jackson.junior\.gemini\antigravity\brain\f054269f-2d9a-43e7-bc43-4642c1efadf9\media__1777576236886.png"
output_path = r"c:\Users\jackson.junior\Documents\Antigravity\Mensageria eSocial\frontend\src\assets\images.ts"

# Ensure directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(img_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

with open(output_path, "w", encoding='utf-8') as f:
    f.write(f'export const BACKGROUND_ESOCIAL = "data:image/png;base64,{encoded_string}";\n')

print(f"Success: {output_path} created.")
