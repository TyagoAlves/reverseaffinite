#include <QApplication>
#include "app_ui.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    app.setApplicationName("reverseaffinite");
    app.setOrganizationName("reverseaffinite");

    MainWindow window;
    window.show();

    return app.exec();
}
