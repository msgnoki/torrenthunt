#include "MainWindow.h"

#include <QApplication>
#include <QList>
#include <QMetaType>

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);

    qRegisterMetaType<TorrentResult>("TorrentResult");
    qRegisterMetaType<QList<TorrentResult>>("QList<TorrentResult>");

    MainWindow window;
    window.resize(1200, 700);
    window.show();

    return app.exec();
}
