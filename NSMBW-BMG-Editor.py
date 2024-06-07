import archive
import sys
import os, os.path
try:
    from PyQt5 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

if hasattr(QtCore, 'pyqtSlot'): # PyQt
    QtCoreSlot = QtCore.pyqtSlot
    QtCoreSignal = QtCore.pyqtSignal
else: # PySide2
    QtCoreSlot = QtCore.Slot
    QtCoreSignal = QtCore.Signal






class BMGString():
    def __init__(self, category, ID):
        """
        Initializes the BMGString
        """
        # set in read_converted_text_bmg where necessary
        #self.string = ''
        #self.attrib
        self.category = category
        self.ID = ID

    def __str__(self):
        out = 'category: {}, ID: {}'.format(self.category, self.ID)
        if hasattr(self, 'attrib'): out += ', attributes: {}'.format(self.attrib)
        if hasattr(self, 'string'): out += ', string: ' + self.string
        return out

    def __repr__(self):
        return str(self)

def create_dict_from_converted_text_bmg():
    with open(os.path.join('tmp', 'wii_mj2d.txt'), 'r') as file:
        txt = file.read().splitlines()

    header = txt[:17]

    messages = {}

    for line in txt[17:-2]:
        number, value = line.lstrip().split('\t')
        number = int(number, 16)
        ID = number & 0xFF
        category = number >> 8
        key = (category, ID)
        if not key in messages:
            messages[key] = BMGString(category, ID)

        if value[0] == '~':
            messages[key].attrib = value[2:]
        elif value[0] == '=':
            messages[key].string = value[2:]
        elif value[0] == '/':
            pass

    return header, messages




def module_path():
    """
    This will get us the program's directory, even if we are frozen
    using PyInstaller
    """

    if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):  # PyInstaller
        if sys.platform == 'darwin':  # macOS
            macos = os.path.dirname(sys.executable)
            if os.path.basename(macos) != 'MacOS':
                return None

            return os.path.join(os.path.dirname(macos), 'Resources')

    if __name__ == '__main__':
        return os.path.dirname(os.path.abspath(sys.argv[0]))

    return None



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle('NSMBW BMG Editor')

        self.setupWidgets()

        self.arc_path = QtWidgets.QFileDialog.getOpenFileName(self, "Open Message.arc", '', "Message File (*.arc)")[0]
        if len(self.arc_path) == 0: sys.exit(0)
        self.get_bmg_from_message_arc(self.arc_path)
        self.convert_bmg_to_txt()
        txt_messages = self.get_converted_txt()
        #txt_messages = '\n'.join(str(m) for m in messages.values())
        self.textbox.setText(txt_messages)



    def get_bmg_from_message_arc(self, path):
        with open(path,'rb') as file:
            data = file.read()

        self.arc = archive.U8()
        self.arc._load(data)

        for key, value in self.arc.files:
            if value is None:
                continue
            elif key == '/wii_mj2d.bmg':
                bmg = self.arc[key]
                if not os.path.exists('tmp'):
                    os.makedirs('tmp')
                with open(os.path.join('tmp', 'wii_mj2d.bmg'), 'wb') as out:
                    out.write(bmg)

    def write_bmg_to_message_arc(self):
        with open(os.path.join('tmp', 'wii_mj2d.bmg'),'rb') as file:
            data = file.read()
        self.arc['/wii_mj2d.bmg'] = data

        outdata = self.arc._dump()
        if outdata is not None:
            with open(self.arc_path, 'wb') as f:
                f.write(outdata)



    def convert_bmg_to_txt(self):
        import subprocess
        child = subprocess.Popen('wbmgt DECODE --overwrite --no-bmg-inline --export --long --single-line '+os.path.join(os.getcwd(), 'tmp', 'wii_mj2d.bmg'), stdout=subprocess.PIPE)
        streamdata = child.communicate()[0]
        rc = child.returncode
        del subprocess
        if rc != 0:
            print("Make sure wbmgt is installed and on PATH!")

    def convert_txt_to_bmg(self):
        import subprocess
        child = subprocess.Popen('wbmgt ENCODE --overwrite '+os.path.join(os.getcwd(), 'tmp', 'wii_mj2d.txt'), stdout=subprocess.PIPE)
        streamdata = child.communicate()[0]
        rc = child.returncode
        del subprocess
        if rc != 0:
            print("Make sure wbmgt is installed and on PATH!")



    def get_converted_txt(self):
        with open(os.path.join('tmp', 'wii_mj2d.txt'), 'r') as file:
            txt = file.read()
        return txt

    def save_edited_txt(self):
        with open(os.path.join('tmp', 'wii_mj2d.txt'), 'w') as file:
            file.write(self.textbox.toPlainText())








    def convLeftFunction(self):
        self.IDBox.setValue(self.numberBox.value() & 0xFF)
        self.categoryBox.setValue(self.numberBox.value() >> 8)


    def convRightFunction(self):
        self.numberBox.setValue(self.categoryBox.value() << 8 | self.IDBox.value())


    def save_to_arc(self):
        self.save_edited_txt()
        self.convert_txt_to_bmg()
        self.write_bmg_to_message_arc()


    def setupWidgets(self):
        self.textbox = QtWidgets.QTextEdit(self)
        self.categoryBox = QtWidgets.QSpinBox(self)
        self.IDBox = QtWidgets.QSpinBox(self)
        self.numberBox = QtWidgets.QSpinBox(self)

        self.categoryBox.setMaximum(2147483647 >> 8)
        self.IDBox.setMaximum(0xFF)
        self.numberBox.setMaximum(2147483647)
        self.numberBox.setDisplayIntegerBase(16)
        spinFont = self.numberBox.font()
        spinFont.setCapitalization(QtGui.QFont.AllUppercase)
        self.numberBox.setFont(spinFont)

        self.convLeft = QtWidgets.QPushButton(self)
        self.convRight = QtWidgets.QPushButton(self)
        self.save = QtWidgets.QPushButton(self)
        self.convLeft.setText('🡐')
        self.convRight.setText('🡒')
        self.save.setText('Save to Message.arc')

        self.convLeft.released.connect(self.convLeftFunction)
        self.convRight.released.connect(self.convRightFunction)
        self.save.released.connect(self.save_to_arc)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.textbox, 0, 0, 1, 5)
        layout.addWidget(self.categoryBox, 1, 0)
        layout.addWidget(self.IDBox, 1, 1)
        layout.addWidget(self.convLeft, 1, 2)
        layout.addWidget(self.convRight, 1, 3)
        layout.addWidget(self.numberBox, 1, 4)
        layout.addWidget(self.save, 2, 0, 1, 5)
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)


#############################################################################################
####################################### Main Function #######################################


if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)

    # go to the script path
    path = module_path()
    if path is not None:
        os.chdir(path)

    with open("dark.qss", 'r') as file:
        qss = file.read()
    app.setStyleSheet(qss)

    try:
        os.makedirs("tmp")
    except FileExistsError:
        pass


    window = MainWindow()

    window.show()
    sys.exit(app.exec_())
    app.deleteLater()
