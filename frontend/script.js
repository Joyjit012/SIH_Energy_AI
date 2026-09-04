// ============================================================
// SMART AI ENERGY MANAGEMENT DASHBOARD
// CLEAN FRONTEND JS
// ============================================================

"use strict";

// ============================================================
// GLOBAL STATE
// ============================================================

let forecastData = [];
let selectedDate = null;

let generationChartInstance = null;
let batteryChartInstance = null;
let generatorChartInstance = null;
let smartChargingChartInstance = null;

const API_BASE = "http://127.0.0.1:8000";


// ============================================================
// PAGE NAVIGATION
// ============================================================

function switchPage(pageId, linkEl) {

    document.querySelectorAll(".page").forEach(page => {
        page.classList.remove("active-page");
        page.classList.add("hidden-page");
    });

    const target = document.getElementById("page-" + pageId);

    if (target) {
        target.classList.remove("hidden-page");
        target.classList.add("active-page");
    }

    document.querySelectorAll(".nav-link").forEach(link => {
        link.classList.remove("active");
    });

    if (linkEl) {
        linkEl.classList.add("active");
    }

    const titles = {
        dashboard: [
            "Dashboard",
            "Renewable Energy Forecast & Optimization"
        ],
        "ai-model": [
            "PolarOps",
            "Station Operations & Energy Intelligence"
        ]
    };

    const title = document.getElementById("pageTitle");
    const subtitle = document.getElementById("pageSubtitle");

    if (titles[pageId]) {

        if (title) {
            title.textContent = titles[pageId][0];
        }

        if (subtitle) {
            subtitle.textContent = titles[pageId][1];
        }
    }

    return false;
}


// ============================================================
// LOAD DATA FROM EDGE SERVER
// ============================================================

async function loadForecastData() {

    console.log("==========================================");
    console.log("Loading EnergyAI data...");
    console.log("Connecting to local Edge AI Server...");
    console.log("==========================================");

    try {

        // ----------------------------------------------------
        // STEP 1 — GET ENERGY RECORDS
        // ----------------------------------------------------

        const response = await fetch(
            `${API_BASE}/api/energy`,
            {
                method: "GET",
                cache: "no-store"
            }
        );

        if (!response.ok) {
            throw new Error(
                `Energy API failed: ${response.status}`
            );
        }

        const result = await response.json();

        console.log("Energy API response:", result);

        if (
            result.status !== "success" ||
            !Array.isArray(result.data)
        ) {
            throw new Error(
                "Invalid data received from Energy API."
            );
        }

        console.log(
            `Records received from server: ${result.data.length}`
        );


        // ----------------------------------------------------
        // STEP 2 — NORMALIZE DATA
        // IMPORTANT: ASSIGN RETURN VALUE
        // ----------------------------------------------------

        forecastData = normalizeEdgeData(result.data);

        console.log(
            `Normalized records: ${forecastData.length}`
        );


        // ----------------------------------------------------
        // STEP 3 — GET DATES
        // ----------------------------------------------------

        let dates = [
            ...new Set(
                forecastData
                    .map(row => row.date)
                    .filter(Boolean)
            )
        ].sort();


        // ----------------------------------------------------
        // STEP 4 — IF DATE FIELD FAILED, ASK SERVER
        // ----------------------------------------------------

        if (dates.length === 0) {

            console.warn(
                "No dates found in normalized data."
            );

            try {

                const dateResponse = await fetch(
                    `${API_BASE}/api/dates`,
                    {
                        method: "GET",
                        cache: "no-store"
                    }
                );

                if (dateResponse.ok) {

                    const dateResult =
                        await dateResponse.json();

                    console.log(
                        "Dates API response:",
                        dateResult
                    );

                    if (
                        dateResult.status === "success" &&
                        Array.isArray(dateResult.dates)
                    ) {

                        dates = dateResult.dates
                            .map(String)
                            .filter(Boolean)
                            .sort();

                        console.log(
                            `Dates received from API: ${dates.length}`
                        );
                    }
                }

            } catch (dateError) {

                console.warn(
                    "Dates API fallback failed:",
                    dateError
                );
            }
        }


        // ----------------------------------------------------
        // STEP 5 — RENDER DATE LIST
        // ----------------------------------------------------

        console.log(
            `Available dates: ${dates.length}`
        );

        console.log(
            "First date:",
            dates[0]
        );

        console.log(
            "Last date:",
            dates[dates.length - 1]
        );


        renderDateList(dates);


        // ----------------------------------------------------
        // STEP 6 — DATE INPUT LIMITS
        // ----------------------------------------------------

        if (dates.length > 0) {

            const minDate = dates[0];
            const maxDate = dates[dates.length - 1];

            [
                "singleDate",
                "startDate",
                "endDate"
            ].forEach(id => {

                const element =
                    document.getElementById(id);

                if (element) {

                    element.min = minDate;
                    element.max = maxDate;
                }
            });
        }


        // ----------------------------------------------------
        // STEP 7 — BUTTONS
        // ----------------------------------------------------

        setupEventListeners();


        // ----------------------------------------------------
        // STEP 8 — STATUS
        // ----------------------------------------------------

        console.log("==========================================");
        console.log("✅ DIGITAL TWIN CONNECTED");
        console.log("✅ Edge data normalized");
        console.log(
            `✅ ${forecastData.length} records loaded`
        );
        console.log(
            `✅ ${dates.length} dates loaded into dashboard`
        );
        console.log("==========================================");


        // Update status badge
        updateSystemStatus(true);

    }

    catch (error) {

        console.error(
            "❌ Failed to load EnergyAI data:",
            error
        );

        updateSystemStatus(false);

        showError(
            "Unable to connect to Edge AI Server. Check that Flask server is running on port 5000."
        );
    }
}


// ============================================================
// NORMALIZE EDGE DATA
// ============================================================

function normalizeEdgeData(data) {

    if (!Array.isArray(data)) {
        return [];
    }

    return data.map(row => {

        const item = { ...row };


        // ----------------------------------------------------
        // TIMESTAMP
        // ----------------------------------------------------

        const timestamp =
            row.timestamp ||
            row.utc_timestamp ||
            row.date_time ||
            row.datetime ||
            row.time_stamp ||
            "";


        item.timestamp = String(timestamp || "");
        item.utc_timestamp = String(timestamp || "");


        // ----------------------------------------------------
        // DATE
        // ----------------------------------------------------

        let date = row.date || "";

        if (!date && timestamp) {

            date = String(timestamp)
                .replace("T", " ")
                .split(" ")[0];
        }

        if (date) {

            date = String(date)
                .trim()
                .split("T")[0]
                .split(" ")[0];
        }

        item.date = date;


        // ----------------------------------------------------
        // TIME
        // ----------------------------------------------------

        let time = row.time || "";

        if (!time && timestamp) {

            const parts =
                String(timestamp)
                    .replace("T", " ")
                    .split(" ");

            if (parts[1]) {
                time = parts[1].substring(0, 5);
            }
        }

        item.time = time || "00:00";


        // ----------------------------------------------------
        // SOLAR
        // Supports multiple backend column names
        // ----------------------------------------------------

        const solar = toNumber(
            row.solar_prediction ??
            row.solar_power ??
            row.solar_generation ??
            row.solar ??
            0
        );


        // ----------------------------------------------------
        // WIND
        // ----------------------------------------------------

        const wind = toNumber(
            row.wind_prediction ??
            row.wind_power ??
            row.wind_generation ??
            row.wind ??
            0
        );


        // ----------------------------------------------------
        // LOAD
        // ----------------------------------------------------

        const load = toNumber(
            row.load_prediction ??
            row.load_power ??
            row.load_demand ??
            row.load ??
            0
        );


        // ----------------------------------------------------
        // RENEWABLE
        // ----------------------------------------------------

        const renewable =
            row.total_renewable !== undefined
                ? toNumber(row.total_renewable)
                : solar + wind;


        item.solar_prediction = solar;
        item.wind_prediction = wind;
        item.total_renewable = renewable;
        item.load_prediction = load;


        // ----------------------------------------------------
        // LOAD PRIORITY
        // ----------------------------------------------------

        item.critical_load =
            toNumber(row.critical_load ?? load * 0.60);

        item.important_load =
            toNumber(row.important_load ?? load * 0.25);

        item.flexible_load =
            toNumber(row.flexible_load ?? load * 0.15);


        // ----------------------------------------------------
        // FLEXIBLE LOAD REDUCTION
        // ----------------------------------------------------

        item.flexible_reduction =
            toNumber(row.flexible_reduction);


        item.optimized_load =
            toNumber(
                row.optimized_load ??
                Math.max(
                    0,
                    load - item.flexible_reduction
                )
            );


        // ----------------------------------------------------
        // RENEWABLE TO LOAD
        // ----------------------------------------------------

        item.renewable_to_load =
            toNumber(
                row.renewable_to_load ??
                Math.min(renewable, load)
            );


        // ----------------------------------------------------
        // BATTERY
        // ----------------------------------------------------

        item.battery_charged =
            toNumber(row.battery_charged);

        item.battery_used =
            toNumber(row.battery_used);

        item.battery_stored =
            toNumber(row.battery_stored);

        item.battery_soc =
            toNumber(
                row.battery_soc ??
                row.soc ??
                50
            );


        // ----------------------------------------------------
        // GENERATOR
        // ----------------------------------------------------

        item.generator =
            toNumber(
                row.generator ??
                row.generator_output
            );


        // ----------------------------------------------------
        // CURTAILED
        // ----------------------------------------------------

        item.curtailed =
            toNumber(row.curtailed);


        // ----------------------------------------------------
        // LOAD SUPPLIED
        // ----------------------------------------------------

        item.load_supplied =
            toNumber(
                row.load_supplied ??
                (
                    Math.min(renewable, load) +
                    item.battery_used +
                    item.generator
                )
            );


        // ----------------------------------------------------
        // ACTION
        // ----------------------------------------------------

        item.action =
            row.action ||
            "Renewable → Load";


        return item;
    });
}


// ============================================================
// NUMBER HELPER
// ============================================================

function toNumber(value) {

    const number = Number(value);

    return Number.isFinite(number)
        ? number
        : 0;
}


// ============================================================
// SYSTEM STATUS
// ============================================================

function updateSystemStatus(online) {

    const possibleIds = [
        "systemStatus",
        "systemStatusText",
        "statusText"
    ];

    possibleIds.forEach(id => {

        const element =
            document.getElementById(id);

        if (!element) return;

        element.textContent =
            online
                ? "System Online"
                : "System Offline";
    });
}


// ============================================================
// EVENT LISTENERS
// ============================================================

function setupEventListeners() {

    const singleModeBtn =
        document.getElementById("singleModeBtn");

    const rangeModeBtn =
        document.getElementById("rangeModeBtn");

    const loadSingleBtn =
        document.getElementById("loadSingleBtn");

    const loadRangeBtn =
        document.getElementById("loadRangeBtn");


    // Prevent duplicate listeners
    if (singleModeBtn) {

        singleModeBtn.onclick = () => {
            switchMode("single");
        };
    }


    if (rangeModeBtn) {

        rangeModeBtn.onclick = () => {
            switchMode("range");
        };
    }


    if (loadSingleBtn) {

        loadSingleBtn.onclick =
            handleSingleDateLoad;
    }


    if (loadRangeBtn) {

        loadRangeBtn.onclick =
            handleRangeDateLoad;
    }


    console.log("✅ Forecast buttons connected");
}


// ============================================================
// MODE SWITCH
// ============================================================

function switchMode(mode) {

    const singleModeBtn =
        document.getElementById("singleModeBtn");

    const rangeModeBtn =
        document.getElementById("rangeModeBtn");

    const singleSection =
        document.getElementById("singleDateSection");

    const rangeSection =
        document.getElementById("rangeDateSection");


    if (mode === "single") {

        singleModeBtn?.classList.add("active");
        rangeModeBtn?.classList.remove("active");

        singleSection?.classList.remove("hidden");
        rangeSection?.classList.add("hidden");

    }

    else {

        rangeModeBtn?.classList.add("active");
        singleModeBtn?.classList.remove("active");

        rangeSection?.classList.remove("hidden");
        singleSection?.classList.add("hidden");
    }
}


// ============================================================
// SINGLE DATE LOAD
// ============================================================

function handleSingleDateLoad() {

    console.log("▶ Single Date button clicked");


    const input =
        document.getElementById("singleDate");


    if (!input || !input.value) {

        alert("Please select a date.");

        return;
    }


    const date = input.value;

    console.log(
        "Selected date:",
        date
    );


    const data =
        forecastData.filter(
            row => row.date === date
        );


    console.log(
        `Records for ${date}: ${data.length}`
    );


    if (data.length === 0) {

        alert(
            `No data available for ${date}`
        );

        return;
    }


    selectedDate = date;

    renderDateList([date]);

    showForecastSection();

    selectDate(date);
}


// ============================================================
// DATE RANGE LOAD
// ============================================================

function handleRangeDateLoad() {

    console.log("▶ Date Range button clicked");


    const startInput =
        document.getElementById("startDate");

    const endInput =
        document.getElementById("endDate");


    if (
        !startInput ||
        !endInput ||
        !startInput.value ||
        !endInput.value
    ) {

        alert(
            "Please select both start and end dates."
        );

        return;
    }


    const start =
        startInput.value;

    const end =
        endInput.value;


    if (end < start) {

        alert(
            "End date cannot be before start date."
        );

        return;
    }


    const rangeData =
        forecastData.filter(
            row =>
                row.date >= start &&
                row.date <= end
        );


    console.log(
        `Range records: ${rangeData.length}`
    );


    if (rangeData.length === 0) {

        alert(
            "No data available for this date range."
        );

        return;
    }


    const dates = [
        ...new Set(
            rangeData.map(row => row.date)
        )
    ].sort();


    renderDateList(dates);

    showForecastSection();

    selectDate(dates[0]);
}


// ============================================================
// DATE LIST
// ============================================================

function renderDateList(dates) {

    const container =
        document.getElementById("dateList");

    const countEl =
        document.getElementById("dateCount");


    // Make sure dates is always an array
    if (!Array.isArray(dates)) {
        dates = [];
    }


    // Remove duplicates
    dates = [
        ...new Set(
            dates
                .map(String)
                .map(d => d.trim())
                .filter(Boolean)
        )
    ].sort();


    // --------------------------------------------------------
    // UPDATE COUNT
    // --------------------------------------------------------

    if (countEl) {

        countEl.textContent =
            `${dates.length} day${dates.length === 1 ? "" : "s"}`;
    }


    // --------------------------------------------------------
    // UPDATE DATE LIST
    // --------------------------------------------------------

    if (!container) {

        console.error(
            "❌ dateList element not found"
        );

        return;
    }


    container.innerHTML = "";


    if (dates.length === 0) {

        container.innerHTML = `
            <div style="
                padding:20px;
                text-align:center;
                color:#9ca3af;
            ">
                No dates available
            </div>
        `;

        return;
    }


    dates.forEach(date => {

        const button =
            document.createElement("button");


        button.type = "button";

        button.className =
            "date-item";


        button.dataset.date =
            date;


        button.innerHTML = `
            <span class="date-text">
                ${formatDate(date)}
            </span>

            <span class="date-arrow">
                ›
            </span>
        `;


        button.onclick = () => {

            console.log(
                "Date clicked:",
                date
            );

            showForecastSection();

            selectDate(date);
        };


        container.appendChild(button);
    });


    console.log(
        `✅ UI rendered ${dates.length} dates`
    );
}


// ============================================================
// FORMAT DATE
// ============================================================

function formatDate(dateString) {

    if (!dateString) {
        return "";
    }


    const date =
        new Date(
            dateString + "T00:00:00"
        );


    if (isNaN(date.getTime())) {
        return dateString;
    }


    return date.toLocaleDateString(
        "en-US",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    );
}


// ============================================================
// SHOW FORECAST SECTION
// ============================================================

function showForecastSection() {

    const section =
        document.getElementById(
            "forecastSection"
        );

    const message =
        document.getElementById(
            "message"
        );


    if (section) {

        section.classList.remove("hidden");
    }


    if (message) {

        message.classList.add("hidden");
    }
}


// ============================================================
// SELECT DATE
// ============================================================

function selectDate(date) {

    console.log(
        "Loading forecast for:",
        date
    );


    selectedDate = date;


    // Highlight selected date

    document
        .querySelectorAll(".date-item")
        .forEach(item => {

            item.classList.toggle(
                "active",
                item.dataset.date === date
            );
        });


    // Get hourly data

    const hourlyData =
        forecastData.filter(
            row => row.date === date
        );


    console.log(
        `Hourly records: ${hourlyData.length}`
    );


    if (hourlyData.length === 0) {

        console.warn(
            "No hourly data for selected date."
        );

        return;
    }


    // Show selected date section

    const section =
        document.getElementById(
            "selectedDateSection"
        );

    if (section) {

        section.classList.remove("hidden");
    }


    // --------------------------------------------------------
    // DAILY SUMMARY
    // --------------------------------------------------------

    showDailySummary(
        date,
        hourlyData
    );


    // --------------------------------------------------------
    // TABLE
    // --------------------------------------------------------

    showHourlyTable(
        hourlyData
    );


    // --------------------------------------------------------
    // CHARTS
    // --------------------------------------------------------

    drawEnergyCharts(
        hourlyData
    );


    // --------------------------------------------------------
    // SMART STATUS
    // --------------------------------------------------------

    updateSmartStatusBar(
        hourlyData
    );


    // --------------------------------------------------------
    // SMART BATTERY
    // --------------------------------------------------------

    const analysis =
        analyzeSmartCharging(
            hourlyData
        );


    updateSmartChargingUI(
        analysis
    );


    drawSmartChargingChart(
        hourlyData,
        analysis
    );
}


// ============================================================
// DAILY SUMMARY
// ============================================================

function showDailySummary(date, data) {

    setText(
        "selectedDateTitle",
        formatDate(date)
    );


    if (!data.length) {
        return;
    }


    const solar =
        sum(data, "solar_prediction");

    const wind =
        sum(data, "wind_prediction");

    const renewable =
        sum(data, "total_renewable");

    const load =
        sum(data, "load_prediction");

    const reduction =
        sum(data, "flexible_reduction");

    const battery =
        sum(data, "battery_used");

    const generator =
        sum(data, "generator");


    const sufficiency =
        load > 0
            ? Math.min(
                100,
                (renewable / load) * 100
            )
            : 100;


    setText(
        "solarTotal",
        `${solar.toFixed(2)} kWh`
    );

    setText(
        "windTotal",
        `${wind.toFixed(2)} kWh`
    );

    setText(
        "renewableTotal",
        `${renewable.toFixed(2)} kWh`
    );

    setText(
        "loadTotal",
        `${load.toFixed(2)} kWh`
    );

    setText(
        "flexibleTotal",
        `${reduction.toFixed(2)} kWh`
    );

    setText(
        "batteryTotal",
        `${battery.toFixed(2)} kWh`
    );

    setText(
        "generatorTotal",
        `${generator.toFixed(2)} kWh`
    );

    setText(
        "sufficiencyTotal",
        `${sufficiency.toFixed(1)}%`
    );
}


// ============================================================
// HOURLY TABLE
// ============================================================

function showHourlyTable(data) {

    const tbody =
        document.getElementById(
            "hourlyTable"
        );

    const hourCount =
        document.getElementById(
            "hourCount"
        );


    if (hourCount) {

        hourCount.textContent =
            `${data.length} hours`;
    }


    if (!tbody) {
        return;
    }


    tbody.innerHTML = "";


    data.forEach((row, index) => {

        const tr =
            document.createElement("tr");


        const value = field =>
            toNumber(
                row[field]
            ).toFixed(2);


        tr.innerHTML = `
            <td>${index + 1}</td>

            <td>${row.time || "-"}</td>

            <td>${value("solar_prediction")}</td>

            <td>${value("wind_prediction")}</td>

            <td>
                <strong>
                    ${value("total_renewable")}
                </strong>
            </td>

            <td>${value("load_prediction")}</td>

            <td>
                ${toNumber(
                    row.battery_soc
                ).toFixed(1)}%
            </td>

            <td>
                ${Math.max(
                    0,
                    toNumber(row.generator)
                ).toFixed(2)}
            </td>

            <td>${value("flexible_reduction")}</td>

            <td>
                <span class="action-badge">
                    ${row.action || "Renewable → Load"}
                </span>
            </td>
        `;


        tbody.appendChild(tr);
    });
}


// ============================================================
// SMART STATUS BAR
// ============================================================

function updateSmartStatusBar(data) {

    if (!data || !data.length) {
        return;
    }


    const batteryAlert =
        document.getElementById(
            "batteryAlertMsg"
        );

    const renewableAlert =
        document.getElementById(
            "renewableAlertMsg"
        );

    const batteryText =
        document.getElementById(
            "batteryAlertText"
        );

    const renewableText =
        document.getElementById(
            "renewableAlertText"
        );


    const last =
        data[data.length - 1];


    const soc =
        toNumber(last.battery_soc);


    const renewable =
        sum(
            data,
            "total_renewable"
        );


    const load =
        sum(
            data,
            "load_prediction"
        );


    if (
        batteryAlert &&
        batteryText
    ) {

        if (soc <= 20) {

            batteryText.textContent =
                `Battery Low: ${soc.toFixed(1)}% — Charge Required`;

            batteryAlert.classList.remove(
                "hidden"
            );

        } else {

            batteryAlert.classList.add(
                "hidden"
            );
        }
    }


    if (
        renewableAlert &&
        renewableText
    ) {

        if (renewable > load) {

            renewableText.textContent =
                `+${(
                    renewable - load
                ).toFixed(2)} kWh Excess — Battery Charging`;

            renewableAlert.classList.remove(
                "hidden"
            );

        } else {

            renewableAlert.classList.add(
                "hidden"
            );
        }
    }
}


// ============================================================
// CHARTS
// ============================================================

function drawEnergyCharts(data) {

    if (
        typeof Chart === "undefined"
    ) {

        console.warn(
            "Chart.js not loaded."
        );

        return;
    }


    const labels =
        data.map(
            row => row.time
        );


    const solar =
        data.map(
            row =>
                toNumber(
                    row.solar_prediction
                )
        );


    const wind =
        data.map(
            row =>
                toNumber(
                    row.wind_prediction
                )
        );


    const renewable =
        data.map(
            row =>
                toNumber(
                    row.total_renewable
                )
        );


    const load =
        data.map(
            row =>
                toNumber(
                    row.load_prediction
                )
        );


    const battery =
        data.map(
            row =>
                toNumber(
                    row.battery_used
                )
        );


    const soc =
        data.map(
            row =>
                toNumber(
                    row.battery_soc
                )
        );


    const generator =
        data.map(
            row =>
                toNumber(
                    row.generator
                )
        );


    // --------------------------------------------------------
    // GENERATION CHART
    // --------------------------------------------------------

    const c1 =
        document.getElementById(
            "generationChart"
        );


    if (c1) {

        if (generationChartInstance) {
            generationChartInstance.destroy();
        }


        generationChartInstance =
            new Chart(
                c1,
                {
                    type: "line",

                    data: {

                        labels,

                        datasets: [

                            {
                                label: "Solar",
                                data: solar,
                                borderColor: "#f59e0b",
                                backgroundColor:
                                    "rgba(245,158,11,0.12)",
                                fill: true,
                                tension: 0.35
                            },

                            {
                                label: "Wind",
                                data: wind,
                                borderColor: "#6366f1",
                                backgroundColor:
                                    "rgba(99,102,241,0.12)",
                                fill: true,
                                tension: 0.35
                            },

                            {
                                label: "Total Renewable",
                                data: renewable,
                                borderColor: "#10b981",
                                borderWidth: 2.5,
                                tension: 0.35
                            },

                            {
                                label: "Load Demand",
                                data: load,
                                borderColor: "#f43f5e",
                                borderDash: [5, 4],
                                tension: 0.35
                            }
                        ]
                    },

                    options: chartOptions(
                        "Energy (kWh)"
                    )
                }
            );
    }


    // --------------------------------------------------------
    // BATTERY CHART
    // --------------------------------------------------------

    const c2 =
        document.getElementById(
            "batteryChart"
        );


    if (c2) {

        if (batteryChartInstance) {
            batteryChartInstance.destroy();
        }


        batteryChartInstance =
            new Chart(
                c2,
                {
                    type: "line",

                    data: {

                        labels,

                        datasets: [

                            {
                                label: "Battery Used (kWh)",
                                data: battery,
                                borderColor: "#6366f1",
                                backgroundColor:
                                    "rgba(99,102,241,0.12)",
                                fill: true,
                                tension: 0.35,
                                yAxisID: "y"
                            },

                            {
                                label: "Battery SOC (%)",
                                data: soc,
                                borderColor: "#06b6d4",
                                borderDash: [3, 3],
                                tension: 0.35,
                                yAxisID: "yPercent"
                            }
                        ]
                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        scales: {

                            y: {
                                beginAtZero: true
                            },

                            yPercent: {

                                min: 0,
                                max: 100,
                                position: "right",

                                grid: {
                                    drawOnChartArea: false
                                }
                            }
                        }
                    }
                }
            );
    }


    // --------------------------------------------------------
    // GENERATOR CHART
    // --------------------------------------------------------

    const c3 =
        document.getElementById(
            "generatorChart"
        );


    if (c3) {

        if (generatorChartInstance) {
            generatorChartInstance.destroy();
        }


        generatorChartInstance =
            new Chart(
                c3,
                {
                    type: "bar",

                    data: {

                        labels,

                        datasets: [

                            {
                                label:
                                    "Generator Output (kWh)",

                                data:
                                    generator,

                                backgroundColor:
                                    "rgba(244,63,94,0.35)",

                                borderColor:
                                    "#f43f5e"
                            }
                        ]
                    },

                    options:
                        chartOptions(
                            "Generator (kWh)"
                        )
                }
            );
    }
}


// ============================================================
// CHART OPTIONS
// ============================================================

function chartOptions(title) {

    return {

        responsive: true,

        maintainAspectRatio: false,

        interaction: {

            intersect: false,

            mode: "index"
        },

        plugins: {

            legend: {

                position: "top"
            }
        },

        scales: {

            y: {

                beginAtZero: true,

                title: {

                    display: true,

                    text: title
                }
            },

            x: {

                grid: {

                    display: false
                }
            }
        }
    };
}


// ============================================================
// SMART BATTERY ANALYSIS
// ============================================================

function analyzeSmartCharging(data) {

    if (
        !data ||
        data.length === 0
    ) {
        return null;
    }


    const hours =
        data.map(
            row => row.time || "--"
        );


    const renewable =
        data.map(
            row =>
                toNumber(
                    row.total_renewable
                )
        );


    const load =
        data.map(
            row =>
                toNumber(
                    row.load_prediction
                )
        );


    const surplus =
        renewable.map(
            (value, index) =>
                value - load[index]
        );


    const socValues = [];

    const stateArr = [];


    let soc =
        Math.max(
            20,
            Math.min(
                95,
                toNumber(
                    data[0].battery_soc
                ) || 50
            )
        );


    const maxLoad =
        Math.max(
            ...load,
            1
        );


    const batteryCapacity =
        maxLoad * 4;


    surplus.forEach(value => {

        if (value > 0) {

            const charge =
                Math.min(
                    value * 0.88,
                    batteryCapacity * 0.12
                );


            soc =
                Math.min(
                    100,
                    soc +
                    (
                        charge /
                        batteryCapacity
                    ) * 100
                );


            stateArr.push(1);

        }

        else if (value < 0) {

            const discharge =
                Math.min(
                    -value * 0.92,
                    batteryCapacity * 0.10
                );


            soc =
                Math.max(
                    20,
                    soc -
                    (
                        discharge /
                        batteryCapacity
                    ) * 100
                );


            stateArr.push(
                soc <= 20
                    ? 0
                    : -1
            );

        }

        else {

            stateArr.push(0);
        }


        socValues.push(
            Number(
                soc.toFixed(2)
            )
        );
    });


    const maxSurplus =
        Math.max(
            ...surplus
        );


    const peakIdx =
        surplus.indexOf(
            maxSurplus
        );


    let advice;


    if (
        surplus[0] > 0
    ) {

        advice =
            "⚡ Optimal charging in progress";

    }

    else if (
        surplus.some(
            value => value > 0
        )
    ) {

        const next =
            surplus.findIndex(
                (value, index) =>
                    index > 0 &&
                    value > 0
            );


        advice =
            `⏳ Wait — surplus charging window opens at ${hours[next]}`;

    }

    else {

        advice =
            "🔴 No surplus today — conserve battery charge";
    }

    let maxLen = 0, currentLen = 0, bestStart = -1, bestEnd = -1, currentStart = -1;
    for (let i = 0; i < surplus.length; i++) {
        if (surplus[i] > 0) {
            if (currentLen === 0) currentStart = i;
            currentLen++;
            if (currentLen > maxLen) {
                maxLen = currentLen;
                bestStart = currentStart;
                bestEnd = i;
            }
        } else {
            currentLen = 0;
        }
    }
    
    let bestWindow = "--";
    if (bestStart !== -1 && bestEnd !== -1) {
        let endIdx = Math.min(hours.length - 1, bestEnd + 1);
        if (bestStart === bestEnd) {
             bestWindow = `${hours[bestStart]}`;
        } else {
             bestWindow = `${hours[bestStart]} - ${hours[bestEnd]}`;
        }
    }

    return {

        hours,

        renewable,

        load,

        surplus,

        socValues,

        stateArr,

        maxSurplus,

        peakIdx,

        maxSoc:
            Math.max(
                ...socValues
            ),

        advice,

        bestWindow
    };
}


// ============================================================
// SMART CHARGING UI
// ============================================================

function updateSmartChargingUI(
    analysis
) {

    if (!analysis) {
        return;
    }


    setText(
        "scPeakSurplus",

        analysis.maxSurplus > 0
            ? `+${analysis.maxSurplus.toFixed(2)} kWh at ${analysis.hours[analysis.peakIdx]}`
            : "No surplus"
    );


    setText(
        "scMaxSoc",

        `${analysis.maxSoc.toFixed(1)}%`
    );


    setText(
        "scAdvice",

        analysis.advice
    );


    setText(
        "scBestWindow",

        analysis.bestWindow || "--"
    );
}


// ============================================================
// SMART CHARGING CHART
// ============================================================

function drawSmartChargingChart(
    data,
    analysis
) {

    if (
        !analysis ||
        typeof Chart === "undefined"
    ) {
        return;
    }


    const canvas =
        document.getElementById(
            "smartChargingChart"
        );


    if (!canvas) {
        return;
    }


    if (smartChargingChartInstance) {

        smartChargingChartInstance.destroy();
    }


    const surplusHighlight =
        analysis.surplus.map(
            v => v > 0 ? analysis.renewable.reduce((a, b) => Math.max(a, b), 0) * 1.15 : null
        );

    smartChargingChartInstance =
        new Chart(
            canvas,
            {
                type: "line",

                data: {

                    labels:
                        analysis.hours,

                    datasets: [

                        {
                            label:
                                "Best Window",

                            data:
                                surplusHighlight,

                            borderColor:
                                "transparent",

                            backgroundColor:
                                "rgba(250, 204, 21, 0.22)",

                            fill: true,

                            pointRadius: 0,

                            tension: 0,

                            spanGaps: false,

                            order: 10
                        },

                        {
                            label:
                                "Renewable Gen (kWh)",

                            data:
                                analysis.renewable,

                            borderColor:
                                "#10b981",

                            backgroundColor:
                                "rgba(16,185,129,0.12)",

                            fill: true,

                            tension: 0.4
                        },

                        {
                            label:
                                "Load Demand (kWh)",

                            data:
                                analysis.load,

                            borderColor:
                                "#f43f5e",

                            borderDash:
                                [6, 4],

                            tension: 0.35
                        },

                        {
                            label:
                                "Battery SOC (%)",

                            data:
                                analysis.socValues,

                            borderColor:
                                "#6366f1",

                            yAxisID:
                                "ySOC",

                            tension:
                                0.4
                        }
                    ]
                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {
                            labels: {
                                filter: function(item) {
                                    return item.text !== "Best Window";
                                }
                            }
                        }
                    },

                    scales: {

                        y: {

                            beginAtZero: true
                        },

                        ySOC: {

                            min: 20,

                            max: 100,

                            position: "right",

                            grid: {
                                drawOnChartArea: false
                            }
                        }
                    }
                },

                plugins: [{
                    id: "surplusHighlight",
                    beforeDraw(chart) {
                        const ctx = chart.ctx;
                        const xAxis = chart.scales.x;
                        const yAxis = chart.scales.y;
                        const surplus = analysis.surplus;

                        if (!surplus || !surplus.length) return;

                        ctx.save();
                        ctx.fillStyle = "rgba(250, 204, 21, 0.18)";

                        for (let i = 0; i < surplus.length; i++) {
                            if (surplus[i] > 0) {
                                const x1 = i === 0
                                    ? xAxis.getPixelForValue(i)
                                    : (xAxis.getPixelForValue(i - 1) + xAxis.getPixelForValue(i)) / 2;
                                const x2 = i === surplus.length - 1
                                    ? xAxis.getPixelForValue(i)
                                    : (xAxis.getPixelForValue(i) + xAxis.getPixelForValue(i + 1)) / 2;

                                ctx.fillRect(
                                    x1,
                                    yAxis.top,
                                    x2 - x1,
                                    yAxis.bottom - yAxis.top
                                );
                            }
                        }

                        ctx.restore();
                    }
                }]
            }
        );
}


// ============================================================
// HELPERS
// ============================================================

function sum(data, field) {

    return data.reduce(
        (total, row) => {

            return total +
                toNumber(
                    row[field]
                );

        },
        0
    );
}


function setText(
    id,
    value
) {

    const element =
        document.getElementById(id);


    if (element) {

        element.textContent =
            value;
    }
}


function showError(message) {

    console.error(
        "Dashboard Error:",
        message
    );


    const element =
        document.getElementById(
            "message"
        );


    if (element) {

        element.textContent =
            message;

        element.classList.remove(
            "hidden"
        );
    }
}


// ============================================================
// INITIALIZE
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        console.log(
            "🚀 Dashboard initialized"
        );

        setupEventListeners();

        loadForecastData();
    }
);