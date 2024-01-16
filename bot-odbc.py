import pyodbc
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Selamat datang!')

def help(update: Update, context: CallbackContext):
    update.message.reply_text('Berikut daftar perintah yang akan membantu anda: \n\n'
                              '/cekstok - Cek stok berdasarkan nama barang dengan perintah /cekstok namabarang \n'
                              'contoh perintah : /cekstok Pulpen standard\n'
                              '/cs - Cek stok berdasarkan nama barang tanpa qty 0 /cs namabarang \n'
                              'contoh perintah : /cs Pulpen standard\n'
                              '/lapor - Untuk lapor bug / error atau kendala lainnya\n\n'
                              'New Feature :\nketikkan nama barang lalu enter di chat otomatis cek stok tanpa perintah /cs')

def default(update: Update, context: CallbackContext):
    update.message.reply_text('Hallo selamat datang. Silakan ketik /help untuk informasi tambahan.')

# Fungsi untuk mengecek stok dari database
def cek_stok(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    input_chat = update.message.text.replace('/cekstok ', '')

    # Koneksi ke database menggunakan DSN pertama (silahkan sesuaikan DSN Kalian)
    dsn1 = "Nama-DSN-1"
    conn1 = pyodbc.connect("DSN=" + dsn1)
    cursor1 = conn1.cursor()

    # Koneksi ke database menggunakan DSN kedua (silahkan sesuaikan DSN Kalian)
    dsn2 = "Nama-DSN-2"
    conn2 = pyodbc.connect("DSN=" + dsn2)
    cursor2 = conn2.cursor()

    try:
        # Query ke tabel DBA.brg dan DBA.grpbrg query ini bisa kalian ubah sesuai kebutuhan kalian dan struktur database kalian
        query = f"""
            SELECT DBA.grpbrg.nmgrp, DBA.brg.nmbrg, DBA.brg.nama, DBA.brg.tipe, ([sawal]+[qty]) AS stock
            FROM DBA.brg
            INNER JOIN DBA.grpbrg ON DBA.brg.nmbrg = DBA.grpbrg.nmbrg
            WHERE DBA.brg.nama LIKE '%{input_chat}%'
        """

        # Eksekusi query untuk DSN pertama
        cursor1.execute(query)
        result1 = cursor1.fetchall()

        # Eksekusi query untuk DSN kedua
        cursor2.execute(query)
        result2 = cursor2.fetchall()

        # Format hasil query untuk DSN pertama
        formatted_result1 = [
            f"[{item[0]}] - {item[1]}\n{item[2]}\nQty: {int(item[4])}" for item in result1
        ]

        # Format hasil query untuk DSN kedua
        formatted_result2 = [
            f"[{item[0]}] - {item[1]}\n{item[2]}\nQty: {int(item[4])}" for item in result2
        ]

        # Check if either result set is empty
        if not result1 and not result2:
            message = f"Data Stock {input_chat} Saat ini Tidak ada / Kosong"
        else:
            # Format hasil query untuk DSN pertama
            formatted_result1 = [
                f"[{item[0]}] - {item[1]}\n{item[2]}\nQty: {int(item[4])}" for item in result1
            ]

            # Format hasil query untuk DSN kedua
            formatted_result2 = [
                f"[{item[0]}] - {item[1]}\n{item[2]}\nQty: {int(item[4])}" for item in result2
            ]

            # Check if either result set is empty and construct the message accordingly
            if not result1:
                message = (
                    f"Berikut Data Stock {input_chat} : \n" + '\n'.join(formatted_result2)
                )
            elif not result2:
                message = (
                    f"Berikut Data Stock {input_chat} : \n" + '\n'.join(formatted_result1)
                )
            else:
                message = (
                    f"Berikut Data Stock {input_chat} : \n" + '\n'.join(formatted_result1) + "\n\n"
                    f"\n" + '\n'.join(formatted_result2)
                )

        # Kirim pesan ke pengguna
        context.bot.send_message(chat_id=user_id, text=message)

    except Exception as e:
        context.bot.send_message(chat_id=user_id, text=f"Error: {str(e)}")

    finally:
        # Tutup koneksi
        conn1.close()
        conn2.close()

def cek_stok_qty_gt_0(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    input_chat = update.message.text.replace('/cs ', '')  # Change command to /cs

    # Koneksi ke database menggunakan DSN pertama (SDKOM-CLOUD)
    dsn1 = "Nama-DSN-1"
    conn1 = pyodbc.connect("DSN=" + dsn1)
    cursor1 = conn1.cursor()

    # Koneksi ke database menggunakan DSN kedua (ARISTON-CLOUD)
    dsn2 = "Nama-DSN-2"
    conn2 = pyodbc.connect("DSN=" + dsn2)
    cursor2 = conn2.cursor()

    try:
        # Query ke tabel DBA.brg dan DBA.grpbrg query ini bisa kalian ubah sesuai struktur data kalian
        query = f"""
            SELECT DBA.grpbrg.nmgrp, DBA.brg.nmbrg, DBA.brg.nama, DBA.brg.tipe, ([sawal]+[qty]) AS stock
            FROM DBA.brg
            INNER JOIN DBA.grpbrg ON DBA.brg.nmbrg = DBA.grpbrg.nmbrg
            WHERE DBA.brg.nama LIKE '%{input_chat}%' AND ([sawal]+[qty]) > 0
        """

        # Eksekusi query untuk DSN pertama
        cursor1.execute(query)
        result1 = cursor1.fetchall()

        # Eksekusi query untuk DSN kedua
        cursor2.execute(query)
        result2 = cursor2.fetchall()

        # Format hasil query untuk DSN pertama
        formatted_result1 = [
            f"[{item[0]}] - {item[1]}\n{item[2]}\nQty: {int(item[4])}" for item in result1
        ]

        # Format hasil query untuk DSN kedua
        formatted_result2 = [
            f"[{item[0]}] - {item[1]}\n{item[2]}\nQty: {int(item[4])}" for item in result2
        ]

        # Check if either result set is empty
        if not result1 and not result2:
            message = f"Data Stock {input_chat} dengan Qty > 0 tidak ditemukan"
        else:
            # Format hasil query untuk DSN pertama
            formatted_result1 = [
                f"[{item[0]}] - {item[1]}\n{item[2]}\nQty: {int(item[4])}" for item in result1
            ]

            # Format hasil query untuk DSN kedua
            formatted_result2 = [
                f"[{item[0]}] - {item[1]}\n{item[2]}\nQty: {int(item[4])}" for item in result2
            ]

            # Check if either result set is empty and construct the message accordingly
            if not result1:
                message = (
                    f"Berikut Data Stock {input_chat} (Tanpa Stock 0) : \n" + '\n'.join(formatted_result2)
                )
            elif not result2:
                message = (
                    f"Berikut Data Stock {input_chat} (Tanpa Stock 0) : \n" + '\n'.join(formatted_result1)
                )
            else:
                message = (
                    f"Berikut Data Stock {input_chat} (Tanpa Stock 0) : \n" + '\n'.join(formatted_result1) + "\n\n"
                    f"\n" + '\n'.join(formatted_result2)
                )

        # Kirim pesan ke pengguna
        context.bot.send_message(chat_id=user_id, text=message)

    except Exception as e:
        context.bot.send_message(chat_id=user_id, text=f"Error: {str(e)}")

    finally:
        # Tutup koneksi
        conn1.close()
        conn2.close()

# Fungsi untuk melaporkan kendala/error/bug
def laporkan(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # Informasi untuk melaporkan kendala/error/bug
    message = (
        "Untuk melaporkan kendala/error/bug, silakan chat ke Developer / Admin. "
        "Terima kasih atas partisipasinya!"
    )

    # Kirim pesan ke pengguna
    context.bot.send_message(chat_id=user_id, text=message)

# Token bot Telegram Anda bisa dibuat di telegram Bot Father
TOKEN = "BOT_TOKEN_ANDA"

# Inisialisasi updater
updater = Updater(token=TOKEN)

# Daftar handler command dan message
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, cek_stok_qty_gt_0))
updater.dispatcher.add_handler(CommandHandler('cekstok', cek_stok))
updater.dispatcher.add_handler(CommandHandler('cs', cek_stok_qty_gt_0))  # Add /cs command
updater.dispatcher.add_handler(CommandHandler('lapor', laporkan))  # Add /lapor command
updater.dispatcher.add_handler(MessageHandler(Filters.command, default))

# Jalankan bot
updater.start_polling()
updater.idle()
