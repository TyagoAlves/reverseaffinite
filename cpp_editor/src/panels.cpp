#include "panels.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QGridLayout>
#include <QColorDialog>

ColorSwatch::ColorSwatch(const QColor &color, QWidget *parent)
    : QPushButton(parent), color_(color)
{
    setFixedSize(32, 32);
    updateStyle();
    connect(this, &QPushButton::clicked, this, [this]() {
        QColor c = QColorDialog::getColor(color_, this);
        if (c.isValid()) {
            setColor(c);
            emit colorPicked(c);
        }
    });
}

void ColorSwatch::setColor(const QColor &c)
{
    color_ = c;
    updateStyle();
}

void ColorSwatch::updateStyle()
{
    setStyleSheet(QString("background-color: %1; border: 2px solid #666; border-radius: 3px;")
                  .arg(color_.name()));
}

ColorPanel::ColorPanel(QWidget *parent)
    : QWidget(parent)
{
    setWindowTitle("Color");
    setMinimumWidth(200);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    auto *swatchLayout = new QHBoxLayout();
    swatchLayout->addWidget(new QLabel("FG:"));
    fgSwatch_ = new ColorSwatch(Qt::black);
    swatchLayout->addWidget(fgSwatch_);
    swatchLayout->addWidget(new QLabel("BG:"));
    bgSwatch_ = new ColorSwatch(Qt::white);
    swatchLayout->addWidget(bgSwatch_);

    auto *swapBtn = new QPushButton("<=>");
    swapBtn->setFixedWidth(36);
    connect(swapBtn, &QPushButton::clicked, this, &ColorPanel::swapColors);
    swatchLayout->addWidget(swapBtn);
    layout->addLayout(swatchLayout);

    connect(fgSwatch_, &ColorSwatch::colorPicked, this, [this](const QColor &c) {
        syncSpins(c);
        emit colorChanged(c);
    });

    auto *hslLabel = new QLabel("<b>HSL</b>");
    layout->addWidget(hslLabel);

    auto *grid = new QGridLayout();
    grid->addWidget(new QLabel("H:"), 0, 0);
    hSpin_ = new QSpinBox(); hSpin_->setRange(0, 360);
    connect(hSpin_, QOverload<int>::of(&QSpinBox::valueChanged), this, &ColorPanel::hslChanged);
    grid->addWidget(hSpin_, 0, 1);

    grid->addWidget(new QLabel("S:"), 1, 0);
    sSpin_ = new QSpinBox(); sSpin_->setRange(0, 100);
    connect(sSpin_, QOverload<int>::of(&QSpinBox::valueChanged), this, &ColorPanel::hslChanged);
    grid->addWidget(sSpin_, 1, 1);

    grid->addWidget(new QLabel("L:"), 2, 0);
    lSpin_ = new QSpinBox(); lSpin_->setRange(0, 100);
    connect(lSpin_, QOverload<int>::of(&QSpinBox::valueChanged), this, &ColorPanel::hslChanged);
    grid->addWidget(lSpin_, 2, 1);

    grid->addWidget(new QLabel("R:"), 3, 0);
    rSpin_ = new QSpinBox(); rSpin_->setRange(0, 255);
    connect(rSpin_, QOverload<int>::of(&QSpinBox::valueChanged), this, &ColorPanel::rgbChanged);
    grid->addWidget(rSpin_, 3, 1);

    grid->addWidget(new QLabel("G:"), 4, 0);
    gSpin_ = new QSpinBox(); gSpin_->setRange(0, 255);
    connect(gSpin_, QOverload<int>::of(&QSpinBox::valueChanged), this, &ColorPanel::rgbChanged);
    grid->addWidget(gSpin_, 4, 1);

    grid->addWidget(new QLabel("B:"), 5, 0);
    bSpin_ = new QSpinBox(); bSpin_->setRange(0, 255);
    connect(bSpin_, QOverload<int>::of(&QSpinBox::valueChanged), this, &ColorPanel::rgbChanged);
    grid->addWidget(bSpin_, 5, 1);

    layout->addLayout(grid);
}

void ColorPanel::syncSpins(const QColor &c)
{
    updating_ = true;
    rSpin_->setValue(c.red());
    gSpin_->setValue(c.green());
    bSpin_->setValue(c.blue());
    hSpin_->setValue(qMax(0, c.hue()));
    sSpin_->setValue(c.saturation());
    lSpin_->setValue(c.lightness());
    updating_ = false;
}

void ColorPanel::swapColors()
{
    QColor fg = fgSwatch_->color();
    QColor bg = bgSwatch_->color();
    fgSwatch_->setColor(bg);
    bgSwatch_->setColor(fg);
    syncSpins(bg);
    emit colorChanged(bg);
}

void ColorPanel::hslChanged()
{
    if (updating_) return;
    QColor c;
    c.setHsl(hSpin_->value(), sSpin_->value(), lSpin_->value());
    updating_ = true;
    rSpin_->setValue(c.red());
    gSpin_->setValue(c.green());
    bSpin_->setValue(c.blue());
    updating_ = false;
    fgSwatch_->setColor(c);
    emit colorChanged(c);
}

void ColorPanel::rgbChanged()
{
    if (updating_) return;
    QColor c(rSpin_->value(), gSpin_->value(), bSpin_->value());
    updating_ = true;
    hSpin_->setValue(qMax(0, c.hue()));
    sSpin_->setValue(c.saturation());
    lSpin_->setValue(c.lightness());
    updating_ = false;
    fgSwatch_->setColor(c);
    emit colorChanged(c);
}
