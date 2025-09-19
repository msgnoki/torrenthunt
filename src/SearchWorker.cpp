#include "SearchWorker.h"

#include <QList>
#include <exception>

SearchWorker::SearchWorker(QObject* parent)
    : QObject(parent) {}

void SearchWorker::performSearch(const QString& query, const QString& site, int page) {
    try {
        if (!client_) {
            client_ = std::make_unique<TorrentSearchClient>();
        }
        QList<TorrentResult> results = client_->search(query, site, page);
        emit searchCompleted(results);
    } catch (const std::exception& ex) {
        emit searchFailed(QString::fromUtf8(ex.what()));
    } catch (...) {
        emit searchFailed(QStringLiteral("Unknown error"));
    }
}
