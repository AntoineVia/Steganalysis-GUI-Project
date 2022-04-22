import os.path
import subprocess
from shutil import rmtree

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QBrush
from PyQt6.QtWidgets import QMainWindow, QTreeWidgetItem, QStyle, QTableWidgetItem

from DeviceList import DeviceList
from ImportFile import ImportFile
from ResultsDisplay import ResultsDisplay


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/gui.ui', self)
        self.selected_device = None
        self.files: list[ImportFile] = []

        self.perform_cleanup()
        self.perform_setup()

    def perform_setup(self):
        """Setup of the main window"""

        # Set window title and icon
        self.setWindowTitle('Image Steganalyzer 1.0')
        self.setWindowIcon(QIcon('assets/src.ico'))

        # Defines the import path from the root directory of the program
        import_path = os.getcwd() + "/imports/"
        self.load_folders(import_path)

        # Defines menu button triggers for the UI
        self.actionImport.triggered.connect(self.choose_and_import)
        self.actionAnalyze_selection.triggered.connect(self.analyze_and_display)

    @staticmethod
    def perform_cleanup():
        """"Perform cleanup"""

        # Removes any previously imported image folders from the imports directory
        imports = 'imports'
        if len(os.listdir(imports)) != 0:
            for directory in os.listdir(imports):
                rmtree('/'.join([os.getcwd(), imports, directory]))

        # Removes any logs left over in the txt directory
        for file in os.listdir('txt'):
            if os.path.isfile(file):
                os.remove(file)

    def choose_and_import(self):
        """Prompt device choice and start import from chosen device"""

        # Creates a list of available Android devices
        self.logView.append("Fetching device list...")
        device_list = self.list_devices()

        # If the list is empty, show an exit message and terminate.
        # If the list only has one device, show a message stating this and automatically choose it
        # If the list has multiple devices, show a window prompting to choose one
        if len(device_list) == 0:
            self.logView.append("No devices available, terminating.")
            return
        elif len(device_list) == 1:
            self.selected_device = device_list[0]
            self.logView.append("Only one device available: {dev}, selecting by default.".format(dev=device_list[0][1]))
        else:
            self.select_device(device_list)

        # If a device has been marked as selected, start the import .jpg files from it
        if self.selected_device:
            self.device_import()
            self.logView.append("Import completed!")

    def analyze_and_display(self):
        """Analyze selected images and display results"""

        # Start image analysis
        self.files = []
        output = self.analyze()
        print(output)

        # If any output is produced, process them
        # Otherwise, return with an error message
        if output:
            header = self.process_output(output)
        else:
            self.logView.append("No file import detected!")
            return

        # Display results
        self.display_results(header)

    def load_folders(self, path):
        """Load imported folders into window file view"""
        for x in range(self.fileView.topLevelItemCount()):
            self.fileView.takeTopLevelItem(x)
        self.load_import_structure(path, self.fileView)

    def load_import_structure(self, startpath, tree):
        """Recursively load all folders / files into window file view"""
        for el in os.listdir(startpath):
            path_info = startpath + "/" + el
            parent_itm = QTreeWidgetItem(tree, [os.path.basename(el)])
            if os.path.isdir(path_info):
                self.load_import_structure(path_info, parent_itm)
                parent_itm.setIcon(0, QStyle.standardIcon(self.style(), QStyle.StandardPixmap.SP_DirIcon))
            else:
                parent_itm.setIcon(0,
                                   QStyle.standardIcon(self.style(), QStyle.StandardPixmap.SP_FileDialogContentsView))

    @staticmethod
    def list_devices():
        """Lists all Android devices available for importing"""
        output = subprocess.run(["adb", "devices", "-l"], text=True, capture_output=True)
        text = output.stdout.split('\n')
        models = []
        devices = []
        for line in text:
            if "List" in line.rstrip() or line == "\n":
                continue
            if line.rstrip():
                devices.append(line.split()[0])
                models.append(line.split()[4].split(":")[1])

        for i in range(len(models)):
            models[i] = models[i].replace("_", " ")

        device_list = list(zip(devices, models))
        return device_list

    def select_device(self, device_list):
        """Shows a device list and prompts user choice"""
        dlg = DeviceList(self)
        for device_id, device_model in device_list:
            dlg.device_list.addItem(device_model)

        if dlg.exec():
            self.selected_device = device_list[dlg.device_list.currentRow()]

    def device_import(self):
        """Import images from selected device"""
        device = self.selected_device[0]
        model = self.selected_device[1]
        with open('./txt/log.txt', 'w') as f:
            f.write("\n=== IMPORT LOG ===\n")
            command = ["sh/pullpics.sh", device, model]
            output = subprocess.run(command, text=True, capture_output=True)
            for line in output.stdout.split('\n'):
                if line.strip():
                    f.write(line)
                    f.write('\n')

        self.load_folders(os.getcwd() + "/imports/")

    @staticmethod
    def get_full_path(item):
        """Get absolute path of file view item"""
        path = (os.getcwd() + '/imports/')
        if item.parent().data():
            path += (item.parent().data() + '/')
        path += item.data()
        return path

    def check_selection(self):
        """Check if selected items are suitable for analysis"""
        current = self.fileView.selectionModel().selectedIndexes()
        if current:
            if len(current) == 1:
                if os.path.isdir(self.get_full_path(current[0])):
                    return 0, self.get_full_path(current[0])  # FOLDER
                else:
                    return 1, self.get_full_path(current[0])  # SINGLE FILE
            else:
                if [os.path.isdir(self.get_full_path(current[i])) for i in range(len(current))].__contains__(True):
                    print("Cannot select files AND folder!")
                    return -1, None  # ERROR
                else:
                    return 2, [self.get_full_path(current[i]) for i in range(len(current))]  # MULTIPLE FILES
        else:
            print("Nothing selected!")
            return -1, None

    def analyze(self):
        """Start analysis of selected files"""
        code, selection = self.check_selection()
        log = './txt/log.txt'

        with open(log, 'a') as f:
            f.write("\n=== ANALYSIS LOG ===\n")
            if code == -1:  # ERROR
                return
            elif code == 0:  # FOLDER
                output = self.analyze_single(selection)
                for file in os.listdir(selection):
                    fullpath = selection + '/' + file
                    file = ImportFile(file, fullpath)
                    self.files.append(file)
            elif code == 1:  # SINGLE FILE
                output = self.analyze_single(selection)
                filename = selection.split('/')[-1]
                self.files.append(ImportFile(filename, selection))
                # print(output)
            elif code == 2:  # MULTIPLE FILES
                output = self.analyze_multiple(selection)
                for path in selection:
                    filename = path.split('/')[-1]
                    file = ImportFile(filename, path)
                    self.files.append(file)

            for line in output.split('\n'):
                if line.strip():
                    f.write(line + '\n')
        return output

    @staticmethod
    def analyze_single(selected):
        """Analyze a single file or folder"""
        output = subprocess.run(['aletheia.py', 'auto', selected], text=True, capture_output=True).stdout
        return output

    @staticmethod
    def analyze_multiple(selected):
        """Analyze multiple files"""
        tmp_path = os.getcwd() + '/imports/.tmp'
        subprocess.run(["mkdir", tmp_path])
        for i in range(len(selected)):
            subprocess.run(["cp", selected[i], tmp_path])
        output = subprocess.run(["aletheia.py", "auto", tmp_path], text=True, capture_output=True).stdout
        return output

    def process_output(self, text):
        """Process the output of the aletheia.py command"""
        tag = "Outguess  Steghide   nsF5  J-UNIWARD *"
        found = False
        text_buffer = []
        dico = {}
        header = ''

        for line in text.split('\n'):
            if not found:
                if line.strip() == tag:
                    found = True
                    header = line.strip()
                    header = header.split()[:-1]
            else:
                text_buffer.append(line.strip())

        tag = "* Probability of being stego using the indicated steganographic method."
        found = False
        txt = ''
        for line in text_buffer:
            if not found:
                if line.strip() == tag:
                    break
                txt += line
                txt += '\n'

        txt = txt.replace('-', '', 59).replace('[', ' ').replace(']', ' ')

        lines = txt.split('\n')

        for i in lines:
            line = i.split()
            tmp = []
            if len(i) != 0:
                for el in line:
                    if "jpg" in el or "..." in el:
                        tmp.append(el)
                        break
                    else:
                        tmp.append(el)
                key = ' '.join(tmp)
                dico[key] = []
                for el in line:
                    try:
                        float(el)
                        dico[key].append(float(el))
                    except ValueError:
                        pass

        for file in self.files:
            name = file.filename
            if len(name) <= 20:
                if name in dico.keys():
                    file.steg_dict = dico[name]
                    file.update()
            else:
                n = name[:17] + '...'
                if n in dico.keys():
                    print(dico[n])
                    file.steg_dict = dico[n]
                    file.update()

        return header

    def display_results(self, header):
        """Display results of analysis in separate window"""
        dlg = ResultsDisplay(self)
        disp = dlg.layout().itemAt(0).widget()
        if len(header) > 0:
            for i in range(len(header)):
                disp.insertColumn(i + 2)
                disp.setHorizontalHeaderLabels(["File", "Steganography detected"] + header)
        else:
            disp.setHorizontalHeaderLabels(["File", "Steganography detected"])

        disp.setRowCount(len(self.files))
        for i in range(len(self.files)):
            item = self.files[i]
            disp.setItem(i, 0, QTableWidgetItem(item.filename))
            disp.setItem(i, 1, QTableWidgetItem("True" if item.steg_detected else "False"))
            if item.steg_detected:
                for j in range(2, disp.columnCount()):
                    disp.setItem(i, j, QTableWidgetItem(str(item.steg_dict[j - 2])))
                    if item.steg_dict[j - 2] >= 0.75:
                        disp.item(i, j).setBackground(QBrush(Qt.GlobalColor.green))
                    elif 0.5 <= item.steg_dict[j - 2] < 0.75:
                        disp.item(i, j).setBackground(QBrush(Qt.GlobalColor.yellow))
                    else:
                        disp.item(i, j).setBackground(QBrush(Qt.GlobalColor.red))
        disp.sortItems(1, Qt.SortOrder.DescendingOrder)
        disp.resizeColumnsToContents()
        dlg.resize(disp.horizontalHeader().length() + 35, 600)
        dlg.exec()
