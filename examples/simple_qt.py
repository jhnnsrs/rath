import sys
from typing import Any

from countries.schema import Countries
from koil.qt import QtKoil
from PyQt5 import QtWidgets
from rath.qt import QtRathQuery

from rath import Rath
from rath.links import compose
from rath.links.aiohttp import AIOHttpLink
from rath.links.validate import ValidatingLink


class QtRathWidget(QtWidgets.QWidget):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.koil = QtKoil(parent=self)
        self.koil.enter()

        public_link = AIOHttpLink(url="https://countries.trevorblades.com/")
        validating_link = ValidatingLink(allow_introspection=True)

        self.rath = Rath(link=compose(validating_link, public_link))
        self.rath.connect()

        self.countries_query = QtRathQuery(Countries, self.rath)

        self.button_greet = QtWidgets.QPushButton("Greet")
        self.greet_label = QtWidgets.QLabel("")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button_greet)
        layout.addWidget(self.greet_label)

        self.setLayout(layout)

        self.button_greet.clicked.connect(self.greet)
        self.countries_query.returned.connect(self.show_countries)
        self.countries_query.errored.connect(print)

    def show_countries(self, c: Countries) -> None:
        print(c)

    def greet(self) -> None:
        self.countries_query.run()


def main(**kwargs: Any) -> None:
    app = QtWidgets.QApplication(sys.argv)
    # app.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))
    main_window = QtRathWidget(**kwargs)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
