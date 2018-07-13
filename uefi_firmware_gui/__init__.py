import sys
import argparse
from PyQt5 import QtGui, QtWidgets
from uefi_firmware.uefi import search_firmware_volumes, FirmwareVolume


class Window(QtWidgets.QWidget):
    def __init__(self, input_data):
        super(Window, self).__init__()
        self.tree = QtWidgets.QTreeView(self)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.tree)
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['GUID'])
        self.tree.setModel(self.model)
        self.import_data(input_data)

    def import_data(self, input_data, root=None):
        if root is None:
            root = self.model.invisibleRootItem()

        volumes = search_firmware_volumes(input_data)

        for index in volumes[1:]:
            data = input_data[index - 40:]
            name = index - 40

            firmware_volume = FirmwareVolume(data, name)
            if not firmware_volume.valid_header or not firmware_volume.process():
                continue

            def iterate_objects(parent, _object, include_content=False):
                for _object in _object.objects:
                    if _object is None:
                        continue
                    _info = _object.info(include_content)
                    parent.appendRow([
                        QtGui.QStandardItem(_info['guid'].upper())
                    ])
                    parent = parent.child(parent.rowCount() - 1)
                    iterate_objects(parent, _object, include_content)

            iterate_objects(root, firmware_volume)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="The file(s) to work on")
    args = parser.parse_args()

    input_data = None
    if args.file:
        try:
            with open(args.file, 'rb') as fh:
                input_data = fh.read()
        except Exception as e:
            print("Error: Cannot read file (%s) (%s)." % (args.file, str(e)))
    else:
        print("Error: No readable files")
        sys.exit()

    app = QtWidgets.QApplication(sys.argv)
    window = Window(input_data)
    window.setGeometry(50, 50, 600, 800)
    window.show()
    sys.exit(app.exec_())
