// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "RTL8814AUDriver",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .library(
            name: "RTL8814AUDriver",
            targets: ["RTL8814AUDriver"]
        ),
        .executable(
            name: "RTL8814AUApp",
            targets: ["RTL8814AUApp"]
        )
    ],
    targets: [
        .target(
            name: "RTL8814AUDriver",
            dependencies: [],
            path: ".",
            exclude: [
                "RTL8814AUAppmain.swift",
                "RTL8814AUDriverBuilder.swift",
                "TestsRTL8814AUDriverTests.swift",
                "RTL8814AUDriverTests.swift",
                "Package.swift"
            ],
            sources: [
                "SharedConstants.swift",
                "RTL8814AUDriverDriver.swift",
                "RTL8814AUDriverNetworkInterface.swift",
                "RTL8814AUDriverUSBInterface.swift",
                "RTL8814AUDriverWiFiInterface.swift",
                "RTL8814AUDriverFirmwareLoader.swift",
                "RTL8814AUDriverRTL8814AUDriver.swift"
            ],
            swiftSettings: [
                // Workaround for macOS 26.2 SDK cyclic dependency
                .unsafeFlags([
                    "-Xfrontend", "-disable-implicit-concurrency-module-import",
                    "-Xfrontend", "-disable-implicit-string-processing-module-import"
                ])
            ]
        ),
        .executableTarget(
            name: "RTL8814AUApp",
            dependencies: [],
            path: ".",
            sources: ["RTL8814AUAppmain.swift"],
            swiftSettings: [
                .unsafeFlags([
                    "-Xfrontend", "-disable-implicit-concurrency-module-import",
                    "-Xfrontend", "-disable-implicit-string-processing-module-import"
                ])
            ]
        ),
        .testTarget(
            name: "RTL8814AUDriverTests",
            dependencies: ["RTL8814AUDriver"],
            path: ".",
            sources: ["TestsRTL8814AUDriverTests.swift"],
            swiftSettings: [
                .unsafeFlags([
                    "-Xfrontend", "-disable-implicit-concurrency-module-import",
                    "-Xfrontend", "-disable-implicit-string-processing-module-import"
                ])
            ]
        )
    ],
    swiftLanguageVersions: [.v5]
)
