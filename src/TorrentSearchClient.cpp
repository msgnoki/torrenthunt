#include "TorrentSearchClient.h"

#include <QEventLoop>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QList>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QUrl>
#include <QUrlQuery>
#include <QVariant>

#include <algorithm>
#include <stdexcept>

namespace {
constexpr int kMaxResults = 50;
const char* kDefaultBaseUrl = "https://torrent-api-py-nx0x.onrender.com";
const char* kUserAgent =
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36";

int valueToInt(const QJsonValue& value) {
    if (value.isDouble()) {
        return value.toInt();
    }
    if (value.isString()) {
        QString number = value.toString().trimmed();
        number.remove(',');
        bool ok = false;
        const int parsed = number.toInt(&ok);
        return ok ? parsed : 0;
    }
    if (value.isNull()) {
        return 0;
    }
    return value.toVariant().toInt();
}

QString firstNonEmpty(const std::initializer_list<QString>& values) {
    for (const auto& value : values) {
        if (!value.trimmed().isEmpty()) {
            return value.trimmed();
        }
    }
    return {};
}

} // namespace

TorrentSearchClient::TorrentSearchClient(QObject* parent)
    : QObject(parent),
      baseUrl_(QString::fromLocal8Bit(qgetenv("TORRENTHUNT_API_URL")).trimmed()),
      apiKey_(QString::fromLocal8Bit(qgetenv("TORRENTHUNT_API_KEY")).trimmed()),
      manager_(new QNetworkAccessManager(this)) {
    if (baseUrl_.isEmpty()) {
        baseUrl_ = QString::fromLatin1(kDefaultBaseUrl);
    }

    while (baseUrl_.endsWith('/')) {
        baseUrl_.chop(1);
    }
}

QList<TorrentResult> TorrentSearchClient::search(const QString& query, const QString& site, int page) {
    if (query.trimmed().isEmpty()) {
        throw std::runtime_error("Search query must not be empty");
    }

    QMap<QString, QString> params;
    params.insert(QStringLiteral("query"), query.trimmed());
    if (!site.trimmed().isEmpty()) {
        params.insert(QStringLiteral("site"), site.trimmed());
    }
    params.insert(QStringLiteral("page"), QString::number(std::max(1, page)));

    const QJsonDocument doc = getJson(QStringLiteral("/api/v1/search"), params);
    return parseSearchResults(doc, site);
}

QVector<SiteInfo> TorrentSearchClient::availableSites() {
    try {
        const QJsonDocument doc = getJson(QStringLiteral("/api/v1/sites/config"));
        QVector<SiteInfo> sites;

        const auto appendSite = [&sites](const QString& slug, const QString& display) {
            const QString safeSlug = slug.trimmed();
            if (safeSlug.isEmpty()) {
                return;
            }
            const QString safeDisplay = display.trimmed().isEmpty() ? safeSlug : display.trimmed();
            sites.push_back({safeSlug, safeDisplay});
        };

        const auto parseSiteObject = [&](const QJsonObject& object) {
            for (auto it = object.begin(); it != object.end(); ++it) {
                const QString slug = it.key();
                if (it->isObject()) {
                    const QJsonObject siteObj = it->toObject();
                    const QString display = firstNonEmpty({
                        siteObj.value(QStringLiteral("website")).toString(),
                        siteObj.value(QStringLiteral("name")).toString(),
                        siteObj.value(QStringLiteral("title")).toString(),
                    });
                    appendSite(slug, display);
                } else if (it->isArray()) {
                    const QJsonArray arr = it->toArray();
                    for (const auto& value : arr) {
                        if (!value.isObject()) {
                            continue;
                        }
                        const QJsonObject siteObj = value.toObject();
                        const QString innerSlug = firstNonEmpty({
                            siteObj.value(QStringLiteral("slug")).toString(),
                            siteObj.value(QStringLiteral("key")).toString(),
                            siteObj.value(QStringLiteral("id")).toString(),
                            slug,
                        });
                        const QString display = firstNonEmpty({
                            siteObj.value(QStringLiteral("website")).toString(),
                            siteObj.value(QStringLiteral("name")).toString(),
                            siteObj.value(QStringLiteral("title")).toString(),
                            innerSlug,
                        });
                        appendSite(innerSlug, display);
                    }
                } else {
                    appendSite(slug, it->toString(slug));
                }
            }
        };

        if (doc.isObject()) {
            const QJsonObject root = doc.object();
            const QJsonValue dataValue = root.value(QStringLiteral("data"));

            if (dataValue.isObject()) {
                parseSiteObject(dataValue.toObject());
            } else if (dataValue.isArray()) {
                for (const auto& value : dataValue.toArray()) {
                    if (!value.isObject()) {
                        continue;
                    }
                    const QJsonObject siteObj = value.toObject();
                    const QString slug = firstNonEmpty({
                        siteObj.value(QStringLiteral("slug")).toString(),
                        siteObj.value(QStringLiteral("key")).toString(),
                        siteObj.value(QStringLiteral("id")).toString(),
                    });
                    const QString display = firstNonEmpty({
                        siteObj.value(QStringLiteral("website")).toString(),
                        siteObj.value(QStringLiteral("name")).toString(),
                        siteObj.value(QStringLiteral("title")).toString(),
                    });
                    appendSite(slug, display);
                }
            } else if (dataValue.isString()) {
                appendSite(dataValue.toString(), dataValue.toString());
            } else if (!dataValue.isUndefined()) {
                parseSiteObject(root);
            } else {
                parseSiteObject(root);
            }
        }

        if (sites.isEmpty()) {
            sites = defaultSites();
        } else {
            std::sort(sites.begin(), sites.end(), [](const SiteInfo& a, const SiteInfo& b) {
                return a.displayName.localeAwareCompare(b.displayName) < 0;
            });
        }

        return sites;
    } catch (const std::exception&) {
        return defaultSites();
    }
}

QUrl TorrentSearchClient::buildUrl(const QString& path, const QMap<QString, QString>& queryParams) const {
    QString normalizedPath = path;
    if (!normalizedPath.startsWith('/')) {
        normalizedPath.prepend('/');
    }

    QUrl url(baseUrl_ + normalizedPath);
    if (!queryParams.isEmpty()) {
        QUrlQuery query;
        for (auto it = queryParams.cbegin(); it != queryParams.cend(); ++it) {
            query.addQueryItem(it.key(), it.value());
        }
        url.setQuery(query);
    }

    return url;
}

QByteArray TorrentSearchClient::get(const QUrl& url) {
    QNetworkRequest request(url);
    request.setHeader(QNetworkRequest::UserAgentHeader, QString::fromLatin1(kUserAgent));
    request.setRawHeader("Accept", "application/json");
    request.setAttribute(QNetworkRequest::RedirectPolicyAttribute,
                         QNetworkRequest::NoLessSafeRedirectPolicy);

    if (!apiKey_.isEmpty()) {
        request.setRawHeader("X-API-Key", apiKey_.toUtf8());
    }

    QNetworkReply* reply = manager_->get(request);
    QEventLoop loop;
    QObject::connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
    loop.exec();

    const QNetworkReply::NetworkError error = reply->error();
    const QByteArray data = reply->readAll();
    const QString errorString = reply->errorString();
    reply->deleteLater();

    if (error != QNetworkReply::NoError) {
        throw std::runtime_error(QStringLiteral("Network request failed: %1").arg(errorString).toStdString());
    }

    return data;
}

QJsonDocument TorrentSearchClient::getJson(const QString& path, const QMap<QString, QString>& queryParams) {
    const QUrl url = buildUrl(path, queryParams);
    const QByteArray payload = get(url);

    QJsonParseError parseError;
    const QJsonDocument doc = QJsonDocument::fromJson(payload, &parseError);
    if (parseError.error != QJsonParseError::NoError) {
        throw std::runtime_error(QStringLiteral("Unable to parse API response: %1")
                                     .arg(parseError.errorString())
                                     .toStdString());
    }

    return doc;
}

QList<TorrentResult> TorrentSearchClient::parseSearchResults(const QJsonDocument& doc, const QString& fallbackSite) {
    QList<TorrentResult> results;

    if (!doc.isObject()) {
        return results;
    }

    const QJsonObject root = doc.object();

    QString errorMessage;
    if (root.contains(QStringLiteral("success")) && !root.value(QStringLiteral("success")).toBool()) {
        errorMessage = root.value(QStringLiteral("error")).toString();
        if (errorMessage.isEmpty()) {
            errorMessage = root.value(QStringLiteral("message")).toString();
        }
    }

    if (errorMessage.isEmpty()) {
        const QJsonValue errorValue = root.value(QStringLiteral("error"));
        if (errorValue.isString()) {
            errorMessage = errorValue.toString();
        } else if (errorValue.isBool() && errorValue.toBool()) {
            errorMessage = root.value(QStringLiteral("message")).toString();
            if (errorMessage.isEmpty()) {
                errorMessage = QStringLiteral("Unknown API error");
            }
        }
    }

    if (!errorMessage.isEmpty()) {
        throw std::runtime_error(errorMessage.toStdString());
    }

    QJsonArray dataArray;
    if (root.value(QStringLiteral("data")).isArray()) {
        dataArray = root.value(QStringLiteral("data")).toArray();
    } else if (root.value(QStringLiteral("results")).isArray()) {
        dataArray = root.value(QStringLiteral("results")).toArray();
    }

    if (dataArray.isEmpty()) {
        return results;
    }

    results.reserve(std::min(kMaxResults, dataArray.size()));

    for (const auto& value : dataArray) {
        if (!value.isObject()) {
            continue;
        }

        const QJsonObject item = value.toObject();
        TorrentResult result;
        result.name = firstNonEmpty({
            item.value(QStringLiteral("name")).toString(),
            item.value(QStringLiteral("title")).toString(),
        });
        if (result.name.isEmpty()) {
            continue;
        }

        result.size = firstNonEmpty({
            item.value(QStringLiteral("size")).toString(),
            item.value(QStringLiteral("filesize")).toString(),
        });

        result.seeders = valueToInt(item.value(QStringLiteral("seeders")));
        result.leechers = valueToInt(item.value(QStringLiteral("leechers")));

        result.uploader = firstNonEmpty({
            item.value(QStringLiteral("uploader")).toString(),
            item.value(QStringLiteral("author")).toString(),
            item.value(QStringLiteral("uploaded_by")).toString(),
        });

        result.magnet = firstNonEmpty({
            item.value(QStringLiteral("magnet")).toString(),
            item.value(QStringLiteral("magnetLink")).toString(),
            item.value(QStringLiteral("magnet_link")).toString(),
        });

        result.url = firstNonEmpty({
            item.value(QStringLiteral("url")).toString(),
            item.value(QStringLiteral("link")).toString(),
            item.value(QStringLiteral("page")).toString(),
        });

        result.site = firstNonEmpty({
            item.value(QStringLiteral("site")).toString(),
            item.value(QStringLiteral("provider")).toString(),
            fallbackSite,
        });

        results.push_back(result);
        if (results.size() >= kMaxResults) {
            break;
        }
    }

    return results;
}

QVector<SiteInfo> TorrentSearchClient::defaultSites() const {
    return {
        {QStringLiteral("1337x"), QStringLiteral("1337x")},
        {QStringLiteral("piratebay"), QStringLiteral("The Pirate Bay")},
        {QStringLiteral("torrentgalaxy"), QStringLiteral("TorrentGalaxy")},
        {QStringLiteral("rarbg"), QStringLiteral("RARBG")},
        {QStringLiteral("nyaa"), QStringLiteral("Nyaa")},
        {QStringLiteral("yts"), QStringLiteral("YTS")},
        {QStringLiteral("eztv"), QStringLiteral("EZTV")},
        {QStringLiteral("torlock"), QStringLiteral("Torlock")},
        {QStringLiteral("bitsearch"), QStringLiteral("Bitsearch")},
    };
}
