#include "MainWindow.h"

#include "SearchWorker.h"

#include <QAction>
#include <QAbstractItemView>
#include <QClipboard>
#include <QComboBox>
#include <QDesktopServices>
#include <QFont>
#include <QUrl>
#include <QGuiApplication>
#include <QHBoxLayout>
#include <QHeaderView>
#include <QLabel>
#include <QLineEdit>
#include <QMenu>
#include <QMessageBox>
#include <QProgressBar>
#include <QPushButton>
#include <QStatusBar>
#include <QTableWidget>
#include <QTableWidgetItem>
#include <QThread>
#include <QVBoxLayout>
#include <QWidget>

namespace {
constexpr int kNameColumn = 0;
constexpr int kSizeColumn = 1;
constexpr int kSeedersColumn = 2;
constexpr int kLeechersColumn = 3;
constexpr int kUploaderColumn = 4;
constexpr int kSiteColumn = 5;
}

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent) {
    setupUi();
    setupConnections();
    setBusyState(false);
    statusBar()->showMessage(tr("Prêt à rechercher..."));

    workerThread_ = new QThread(this);
    worker_ = new SearchWorker();
    worker_->moveToThread(workerThread_);

    connect(workerThread_, &QThread::finished, worker_, &QObject::deleteLater);
    connect(this, &MainWindow::requestSearch, worker_, &SearchWorker::performSearch, Qt::QueuedConnection);
    connect(worker_, &SearchWorker::searchCompleted, this, &MainWindow::handleSearchCompleted, Qt::QueuedConnection);
    connect(worker_, &SearchWorker::searchFailed, this, &MainWindow::handleSearchFailed, Qt::QueuedConnection);

    workerThread_->start();
}

MainWindow::~MainWindow() {
    if (workerThread_) {
        workerThread_->quit();
        workerThread_->wait();
    }
}

void MainWindow::setupUi() {
    auto* central = new QWidget(this);
    auto* mainLayout = new QVBoxLayout(central);
    mainLayout->setContentsMargins(12, 12, 12, 12);
    mainLayout->setSpacing(12);

    auto* title = new QLabel(tr("🔍 TorrentHunt Desktop"), this);
    QFont titleFont = title->font();
    titleFont.setPointSize(18);
    titleFont.setBold(true);
    title->setFont(titleFont);
    title->setAlignment(Qt::AlignHCenter);
    mainLayout->addWidget(title);

    auto* searchCard = new QWidget(this);
    searchCard->setObjectName(QStringLiteral("searchCard"));
    auto* searchLayout = new QHBoxLayout(searchCard);
    searchLayout->setContentsMargins(16, 16, 16, 16);
    searchLayout->setSpacing(10);

    siteCombo_ = new QComboBox(searchCard);

    searchEdit_ = new QLineEdit(searchCard);
    searchEdit_->setPlaceholderText(tr("Entrez votre recherche"));

    searchButton_ = new QPushButton(tr("Rechercher"), searchCard);

    progressBar_ = new QProgressBar(searchCard);
    progressBar_->setRange(0, 0);
    progressBar_->setVisible(false);
    progressBar_->setTextVisible(false);

    searchLayout->addWidget(new QLabel(tr("Site:"), searchCard));
    searchLayout->addWidget(siteCombo_);
    searchLayout->addSpacing(12);
    searchLayout->addWidget(new QLabel(tr("Recherche:"), searchCard));
    searchLayout->addWidget(searchEdit_, 1);
    searchLayout->addWidget(searchButton_);
    searchLayout->addWidget(progressBar_);

    mainLayout->addWidget(searchCard);

    resultsTable_ = new QTableWidget(this);
    resultsTable_->setColumnCount(6);
    resultsTable_->setHorizontalHeaderLabels({
        tr("Nom du torrent"),
        tr("Taille"),
        tr("Seeders"),
        tr("Leechers"),
        tr("Uploader"),
        tr("Site")});
    resultsTable_->horizontalHeader()->setStretchLastSection(true);
    resultsTable_->setSelectionBehavior(QAbstractItemView::SelectRows);
    resultsTable_->setSelectionMode(QAbstractItemView::SingleSelection);
    resultsTable_->setEditTriggers(QAbstractItemView::NoEditTriggers);
    resultsTable_->setContextMenuPolicy(Qt::CustomContextMenu);
    resultsTable_->verticalHeader()->setVisible(false);
    resultsTable_->horizontalHeader()->setSectionResizeMode(kNameColumn, QHeaderView::Stretch);
    resultsTable_->horizontalHeader()->setSectionResizeMode(kSizeColumn, QHeaderView::ResizeToContents);
    resultsTable_->horizontalHeader()->setSectionResizeMode(kSeedersColumn, QHeaderView::ResizeToContents);
    resultsTable_->horizontalHeader()->setSectionResizeMode(kLeechersColumn, QHeaderView::ResizeToContents);
    resultsTable_->horizontalHeader()->setSectionResizeMode(kUploaderColumn, QHeaderView::ResizeToContents);
    resultsTable_->horizontalHeader()->setSectionResizeMode(kSiteColumn, QHeaderView::ResizeToContents);

    mainLayout->addWidget(resultsTable_, 1);

    setCentralWidget(central);

    contextMenu_ = new QMenu(this);
    contextMenu_->addAction(tr("Copier le lien magnet"), this, &MainWindow::copyMagnet);
    contextMenu_->addAction(tr("Ouvrir dans le navigateur"), this, &MainWindow::openInBrowser);
    contextMenu_->addSeparator();
    contextMenu_->addAction(tr("Télécharger avec le client par défaut"), this, &MainWindow::openMagnet);

    loadSiteConfig();
}

void MainWindow::setupConnections() {
    connect(searchButton_, &QPushButton::clicked, this, &MainWindow::triggerSearch);
    connect(searchEdit_, &QLineEdit::returnPressed, this, &MainWindow::triggerSearch);
    connect(resultsTable_, &QTableWidget::customContextMenuRequested, this, &MainWindow::showContextMenu);
    connect(resultsTable_, &QTableWidget::cellDoubleClicked, this, &MainWindow::handleDoubleClick);
}

void MainWindow::loadSiteConfig() {
    TorrentSearchClient client;
    sites_ = client.availableSites();

    siteDisplayBySlug_.clear();
    siteCombo_->clear();

    for (const auto& site : sites_) {
        siteCombo_->addItem(site.displayName, site.slug);
        siteDisplayBySlug_.insert(site.slug, site.displayName);
    }

    if (siteCombo_->count() == 0) {
        siteCombo_->addItem(QStringLiteral("1337x"), QStringLiteral("1337x"));
        siteDisplayBySlug_.insert(QStringLiteral("1337x"), QStringLiteral("1337x"));
    }

    siteCombo_->setCurrentIndex(0);
}

void MainWindow::triggerSearch() {
    const QString query = searchEdit_->text().trimmed();
    if (query.isEmpty()) {
        QMessageBox::warning(this, tr("Attention"), tr("Veuillez entrer un terme de recherche"));
        return;
    }

    QString site = siteCombo_->currentData().toString().trimmed();
    if (site.isEmpty()) {
        site = siteCombo_->currentText().trimmed();
    }

    setBusyState(true);
    statusBar()->showMessage(tr("Recherche de '%1' sur %2...").arg(query, displayNameForSite(site)));
    emit requestSearch(query, site, 1);
}

void MainWindow::handleSearchCompleted(const QList<TorrentResult>& results) {
    currentResults_ = results;
    populateResults(results);
    setBusyState(false);

    const int count = results.size();
    statusBar()->showMessage(tr("%1 torrent(s) trouvé(s)").arg(count));
    if (count == 0) {
        QMessageBox::information(this, tr("Information"), tr("Aucun résultat trouvé pour cette recherche"));
    }
}

void MainWindow::handleSearchFailed(const QString& errorMessage) {
    setBusyState(false);
    statusBar()->showMessage(tr("Erreur lors de la recherche"));
    QMessageBox::critical(this, tr("Erreur"), errorMessage);
}

void MainWindow::showContextMenu(const QPoint& position) {
    if (selectedRow() < 0) {
        return;
    }
    contextMenu_->popup(resultsTable_->viewport()->mapToGlobal(position));
}

void MainWindow::copyMagnet() {
    const int row = selectedRow();
    if (row < 0 || row >= currentResults_.size()) {
        return;
    }

    const QString magnet = currentResults_.at(row).magnet;
    if (magnet.isEmpty()) {
        QMessageBox::information(this, tr("Information"), tr("Lien magnet indisponible pour cette entrée"));
        return;
    }

    QGuiApplication::clipboard()->setText(magnet);
    statusBar()->showMessage(tr("Lien magnet copié"), 3000);
}

void MainWindow::openInBrowser() {
    const int row = selectedRow();
    if (row < 0 || row >= currentResults_.size()) {
        return;
    }

    const auto& result = currentResults_.at(row);
    if (result.url.isEmpty()) {
        QMessageBox::information(this, tr("Information"), tr("Aucune URL disponible pour cette entrée"));
        return;
    }

    QDesktopServices::openUrl(QUrl(result.url));
    statusBar()->showMessage(tr("Ouverture dans le navigateur"), 3000);
}

void MainWindow::openMagnet() {
    const int row = selectedRow();
    if (row < 0 || row >= currentResults_.size()) {
        return;
    }

    const auto& result = currentResults_.at(row);
    if (result.magnet.isEmpty()) {
        QMessageBox::information(this, tr("Information"), tr("Lien magnet indisponible pour cette entrée"));
        return;
    }

    QDesktopServices::openUrl(QUrl(result.magnet));
    statusBar()->showMessage(tr("Ouverture du client torrent..."), 3000);
}

void MainWindow::handleDoubleClick(int row, int /*column*/) {
    resultsTable_->selectRow(row);
    copyMagnet();
}

void MainWindow::populateResults(const QList<TorrentResult>& results) {
    resultsTable_->clearContents();
    resultsTable_->setRowCount(results.size());

    for (int row = 0; row < results.size(); ++row) {
        const auto& item = results.at(row);

        auto* nameItem = new QTableWidgetItem(item.name);
        auto* sizeItem = new QTableWidgetItem(item.size);
        auto* seedersItem = new QTableWidgetItem(QString::number(item.seeders));
        auto* leechersItem = new QTableWidgetItem(QString::number(item.leechers));
        auto* uploaderItem = new QTableWidgetItem(item.uploader);
        auto* siteItem = new QTableWidgetItem(displayNameForSite(item.site));

        resultsTable_->setItem(row, kNameColumn, nameItem);
        resultsTable_->setItem(row, kSizeColumn, sizeItem);
        resultsTable_->setItem(row, kSeedersColumn, seedersItem);
        resultsTable_->setItem(row, kLeechersColumn, leechersItem);
        resultsTable_->setItem(row, kUploaderColumn, uploaderItem);
        resultsTable_->setItem(row, kSiteColumn, siteItem);
    }
}

void MainWindow::setBusyState(bool busy) {
    searchButton_->setEnabled(!busy);
    searchEdit_->setEnabled(!busy);
    siteCombo_->setEnabled(!busy);
    progressBar_->setVisible(busy);
    if (busy) {
        progressBar_->setRange(0, 0);
    } else {
        progressBar_->setRange(0, 1);
        progressBar_->setValue(0);
    }
}

int MainWindow::selectedRow() const {
    return resultsTable_->currentRow();
}

QString MainWindow::displayNameForSite(const QString& slug) const {
    const QString key = slug.trimmed();
    if (key.isEmpty()) {
        return slug;
    }
    return siteDisplayBySlug_.value(key, key);
}
