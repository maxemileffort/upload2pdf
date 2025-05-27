# import streamlit as st
# from pydrive2.auth import GoogleAuth
# from pydrive2.drive import GoogleDrive
# import os
# import io
# from PIL import Image
# from PyPDF2 import PdfMerger
# from datetime import datetime

# def authenticate_google_drive():
#     gauth = GoogleAuth()
#     gauth.LoadClientConfigFile("client_secrets.json")
#     gauth.LocalWebserverAuth()
#     drive = GoogleDrive(gauth)
#     return drive

# def list_drive_files(drive, parent_id='root'):
#     file_list = drive.ListFile({'q': f"'{parent_id}' in parents and trashed=false"}).GetList()
#     return file_list

# def download_images(drive, folder_id):
#     image_extensions = ['.jpg', '.png', '.jpeg']
#     images = []
    
#     def recursive_fetch(folder_id, path):
#         items = list_drive_files(drive, folder_id)
#         for item in items:
#             if item['mimeType'] == 'application/vnd.google-apps.folder':
#                 recursive_fetch(item['id'], os.path.join(path, item['title']))
#             elif any(item['title'].lower().endswith(ext) for ext in image_extensions):
#                 # Use a local path to save the image
#                 local_path = os.path.join(path, item['title'])
#                 item.GetContentFile(local_path)  # Save the file locally
#                 images.append(local_path)  # Append the local file path
    
#     recursive_fetch(folder_id, "")
#     return images

# def create_pdf(image_paths, output_path="output.pdf"):
#     pdf_merger = PdfMerger()
#     temp_images = []
    
#     for image_path in image_paths:
#         img = Image.open(image_path).convert("RGB")
#         temp_file = f"temp_{os.path.basename(image_path)}.pdf"
#         img.save(temp_file, "PDF", resolution=100.0)
#         pdf_merger.append(temp_file)
#         temp_images.append(temp_file)

#     today_str = datetime.today().strftime('%Y-%m-%d')
#     final_output_path = output_path.replace('.pdf', f'_{today_str}.pdf')
#     pdf_merger.write(output_path)
#     pdf_merger.close()
    
#     for temp in temp_images:
#         os.remove(temp)
    
#     return output_path

# def main():
#     st.title("Google Drive Image to PDF Generator")
    
#     if st.button("Connect to Google Drive"):
#         drive = authenticate_google_drive()
#         st.session_state['drive'] = drive
#         st.success("Connected to Google Drive!")
    
#     if 'drive' in st.session_state:
#         drive = st.session_state['drive']
#         folders = list_drive_files(drive)
        
#         folder_options = {f['title']: f['id'] for f in folders if f['mimeType'] == 'application/vnd.google-apps.folder'}
#         selected_folder = st.selectbox("Select a folder:", list(folder_options.keys()))
        
#         if st.button("Download Images & Create PDF"):
#             images = download_images(drive, folder_options[selected_folder])
#             pdf_path = create_pdf(images)
            
#             st.success("PDF Created Successfully!")
#             with open(pdf_path, "rb") as pdf_file:
#                 st.download_button("Download PDF", pdf_file, file_name="output.pdf", mime="application/pdf")

# if __name__ == "__main__":
#     main()

import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
import io
from PIL import Image, ImageDraw, ImageFont
from PyPDF2 import PdfMerger
from datetime import datetime

def authenticate_google_drive():
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile("client_secrets.json")
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive

def list_drive_files(drive, parent_id='root'):
    file_list = drive.ListFile({'q': f"'{parent_id}' in parents and trashed=false"}).GetList()
    return file_list

def download_images(drive, folder_id):
    image_extensions = ['.jpg', '.png', '.jpeg']
    images = []
    
    def recursive_fetch(folder_id, path):
        items = list_drive_files(drive, folder_id)
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                recursive_fetch(item['id'], os.path.join(path, item['title']))
            elif any(item['title'].lower().endswith(ext) for ext in image_extensions):
                local_path = os.path.join(path, item['title'])
                item.GetContentFile(local_path)
                images.append((path, local_path))
    
    recursive_fetch(folder_id, "")
    return images

def stamp_image(image_path, text):
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    text_position = (10, 10)
    draw.text(text_position, text, fill=(255, 0, 0), font=font)
    stamped_path = f"stamped_{os.path.basename(image_path)}"
    img.save(stamped_path)
    return stamped_path

def create_pdf(image_data, output_path="output.pdf"):
    pdf_merger = PdfMerger()
    temp_images = []
    
    for folder, image_path in image_data:
        stamped_image = stamp_image(image_path, os.path.basename(image_path))
        img = Image.open(stamped_image).convert("RGB")
        temp_file = f"temp_{os.path.basename(image_path)}.pdf"
        img.save(temp_file, "PDF", resolution=100.0)
        pdf_merger.append(temp_file)
        temp_images.append(temp_file)
    
    today_str = datetime.today().strftime('%Y-%m-%d')
    final_output_path = output_path.replace('.pdf', f'_{today_str}.pdf')
    pdf_merger.write(final_output_path)
    pdf_merger.close()
    
    for temp in temp_images:
        os.remove(temp)
    
    return final_output_path

def main():
    st.title("Google Drive Image to PDF Generator")
    
    if st.button("Connect to Google Drive"):
        drive = authenticate_google_drive()
        st.session_state['drive'] = drive
        st.success("Connected to Google Drive!")
    
    if 'drive' in st.session_state:
        drive = st.session_state['drive']
        folders = list_drive_files(drive)
        folder_options = {f['title']: f['id'] for f in folders if f['mimeType'] == 'application/vnd.google-apps.folder'}
        
        selected_date = st.date_input("Select a date:")
        date_str = selected_date.strftime("%Y-%m-%d")
        
        filtered_folders = {name: fid for name, fid in folder_options.items() if date_str in name}
        selected_folder = st.selectbox("Select a folder:", list(filtered_folders.keys()))
        
        if st.button("Download Images & Create PDF"):
            images = download_images(drive, filtered_folders[selected_folder])
            pdf_path = create_pdf(images)
            
            st.success("PDF Created Successfully!")
            with open(pdf_path, "rb") as pdf_file:
                st.download_button("Download PDF", pdf_file, file_name=pdf_path, mime="application/pdf")

if __name__ == "__main__":
    main()
