set(SOURCES
    main.cpp
    MainWindow.cpp
    TorrentSearchClient.cpp
    SearchWorker.cpp
)

set(HEADERS
    ../include/MainWindow.h
    ../include/TorrentSearchClient.h
    ../include/SearchWorker.h
)

add_executable(torrenthunt_desktop ${SOURCES} ${HEADERS})

target_include_directories(torrenthunt_desktop PRIVATE ../include)

target_link_libraries(torrenthunt_desktop PRIVATE ${QT_LIBS})

if(WIN32)
    set_property(TARGET torrenthunt_desktop PROPERTY WIN32_EXECUTABLE TRUE)
endif()
