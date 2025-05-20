import socket
import json
import base64
import logging
import os

server_address = ('172.16.16.101', 7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message")

        if not command_str.endswith("\r\n\r\n"):
            command_str += "\r\n\r\n"

        sock.sendall(command_str.encode())

        data_received = ""
        while True:
            data = sock.recv(16)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break

        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except Exception as e:
        logging.warning(f"error during data receiving: {e}")
        return False

def remote_list():
    command_str = "LIST"
    hasil = send_command(command_str)
    if hasil['status'] == 'OK':
        print("Daftar file:")
        for f in hasil['data']:
            print(f"- {f}")
        return True
    else:
        print("Gagal mengambil daftar file.")
        return False

def remote_get(filename=""):
    command_str = f"GET {filename}"
    hasil = send_command(command_str)
    if hasil['status'] == 'OK':
        namafile = hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        filepath = os.path.join('files', namafile)
        with open(filepath, 'wb') as f:
            f.write(isifile)
        print(f"File {namafile} berhasil diunduh ke folder files/.")
        return True
    else:
        print(f"Gagal mengunduh file: {hasil['data']}")
        return False

def remote_upload(filepath):
    try:
        filename = os.path.basename(filepath)
        fullpath = os.path.join('files', filename)
        with open(fullpath, 'rb') as f:
            filedata = base64.b64encode(f.read()).decode()
        payload = json.dumps({
            "command": "upload",
            "filename": filename,
            "filedata": filedata
        }) + "\r\n\r\n"
        hasil = send_command(payload)
        if hasil['status'] == 'OK':
            print(f"Upload berhasil: {hasil['data']}")
        else:
            print(f"Gagal upload: {hasil['data']}")
    except Exception as e:
        print(f"Error saat upload: {e}")

def remote_delete(filename):
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str)
    if hasil['status'] == 'OK':
        print(f"File {filename} berhasil dihapus.")
    else:
        print(f"Gagal menghapus file: {hasil['data']}")

if __name__ == '__main__':
    # Contoh penggunaan otomatis:
    
    remote_list()  # Menampilkan daftar file

    remote_get("file.txt")

    remote_upload("aiueo.txt")

    remote_delete("file.txt")

    remote_list()
