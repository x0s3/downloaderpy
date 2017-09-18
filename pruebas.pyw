import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import QUrl, QFileInfo, QFile, QIODevice
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

class Dialogo(QMainWindow):
 def __init__(self):
  QMainWindow.__init__(self)
  uic.loadUi("pruebas.ui", self)
  #Almacena la url del archivo a descargar
  self.url = None
  #Almacena el manejador del fichero a crear
  self.file = None
  #almacena el nombre del archivo a descargar
  self.filename = None
  #almacena en su caso el error en un string
  self.errorString = None
  #almacena en su caso el número de error
  self.errorCode = None
  #Objeto para establecer la conexión y crear el objeto QNetworkReply
  self.http = QNetworkAccessManager(self)
  #Desactivar los botones de descargar y cancelar en un principio
  self.descargar.setEnabled(False)
  self.cancelar.setEnabled(False)
  self.setWindowTitle('Descargar archivos')
  self.progreso.hide()
  #Establece si los botones están activos o no
  self.btn_active = False
  
  #Inicia todo el proceso de descarga
  self.descargar.clicked.connect(self.download)
  #Cancela la descarga
  self.cancelar.clicked.connect(self.cancel_download)
  #Detectar el cambio de texto en el campo de texto para activar el botón de descarga
  self.link_url.textChanged.connect(self.btn_enabled)
  
 #Detectar el cambio de texto en el campo de texto para activar el botón de descarga
 def btn_enabled(self):
  if self.link_url.text() != "":
   self.btn_active = True
   self.descargar.setEnabled(True)
  else:
   self.btn_active = False
 
 #Inicia todo el proceso de descarga
 def download(self):
  if self.btn_active == True:
   #link_url indicada por el usuario
   link_url = self.link_url.text()
   self.url = QUrl(link_url)
   fileinfo = QFileInfo(self.url.path())
   self.filename = fileinfo.fileName()
   #Manejador del fichero
   self.file = QFile(self.filename)
   #Si no es posible crear el fichero
   if not self.file.open(QIODevice.WriteOnly): 
    self.estado.setText("No se pudo crear el archivo")
    self.file.close()
   else: #Entonces llamar al método que inicia la descarga del archivo
    self.start_download()

 
 #Inicia el proceso de descarga y controla las diferente señales (eventos) durante la misma
 def start_download(self):
  #Objeto QNetworkReply
  self.descargar.setEnabled(False)
  self.progreso.show()
  self.reply = self.http.get(QNetworkRequest(self.url))
  self.estado.setText("Iniciando la descarga ...")
  #Empieza la lectura del archivo remoto y escritura local
  self.reply.readyRead.connect(self.ready_read)
  #Señal predefinida para obtener los bytes en el proceso descarga y asignarlos al progreso
  self.reply.downloadProgress.connect(self.updateDataReadProgress)
  #Señal para capturar posibles errores durante la descarga
  self.reply.error.connect(self.error_download)
  #Finalización de la descarga
  self.reply.finished.connect(self.finished_download)
 
 #Ocurre durante la escritura del archivo
 def ready_read(self):
  #Escritura del archivo local
  self.file.write(self.reply.readAll())
  self.estado.setText("Descargando...")
  #Activación del botón de cancelar
  self.cancelar.setEnabled(True)
 
 #Método predefinido en la clase QNetworkReply para leer el progreso de descarga
 def updateDataReadProgress(self, bytesRead, totalBytes):
  self.progreso.setMaximum(totalBytes)
  self.progreso.setValue(bytesRead)
 
 #Si ha ocurrido algún error durante el proceso de descarga
 def error_download(self, error):
  #Si ha ocurrido un error, mostrar el error e eliminar el archivo en el método finished_download
  self.errorString = self.reply.errorString()
  self.errorCode = error
 
 #Ocurre cuando la descarga ha finalizado
 def finished_download(self):
  #Si existe un error
  if self.errorCode is not None:
   #Poner a 0 el progreso
   self.progreso.setValue(0)
   self.estado.setText(str(self.errorCode) + ": " + self.errorString)
   #Eliminar el archivo
   self.file.remove()
  else:
   self.progreso.setValue(0)
   self.estado.setText("Descarga completada")
  
  #Cerrar el fichero
  self.file.close()
  #Desactivar el botón de cancelar ya que la descarga ha finalizado
  self.cancelar.setEnabled(False)
  #Restaurar a None los valores de los atributos de error
  self.errorString = None
  self.errorCode = None
    
 #Cancelar la descargar durante su ejecución
 def cancel_download(self):
  #Abortar la descarga
  self.reply.abort()
  #Desconectar del servidor
  self.reply.close()
  #Eliminar el fichero
  self.file.remove()
  #Cerrar el fichero
  self.file.close()
  #Informamos al usuario de que la descarga se ha cancelado
  self.estado.setText("Descarga cancelada, archivo eliminado")
 
app = QApplication(sys.argv)
dialogo = Dialogo()
dialogo.show()
app.exec_()