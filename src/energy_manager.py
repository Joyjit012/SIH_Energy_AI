# ==========================================
# SIMPLE SMART ENERGY MANAGER
# ==========================================

import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

MIN_SOC = 20.0
MAX_SOC = 100.0

CHARGE_EFFICIENCY = 0.90
DISCHARGE_EFFICIENCY = 0.90


# ==========================================
# LOAD PRIORITY
# ==========================================

CRITICAL_PERCENT = 0.60
IMPORTANT_PERCENT = 0.25
FLEXIBLE_PERCENT = 0.15


# ==========================================
# FLEXIBLE LOAD REDUCTION
# ==========================================

def get_flexible_reduction(soc):

    if soc > 40:
        return 0.00

    elif soc > 30:
        return 0.25

    elif soc > 20:
        return 0.50

    else:
        return 0.70


# ==========================================
# INITIALIZE BATTERY
# ==========================================

def initialize_battery(
    battery_capacity,
    initial_soc
):

    battery_capacity = max(
        0.0,
        float(battery_capacity)
    )

    initial_soc = max(
        MIN_SOC,
        min(
            MAX_SOC,
            float(initial_soc)
        )
    )

    return (
        battery_capacity *
        initial_soc /
        100.0
    )


# ==========================================
# SMART ENERGY MANAGEMENT
# ==========================================

def manage_energy(
    solar,
    wind,
    load,
    stored_energy,
    battery_capacity
):

    # ======================================
    # CLEAN INPUT
    # ======================================

    solar = max(0.0, float(solar))
    wind = max(0.0, float(wind))
    load = max(0.0, float(load))

    battery_capacity = max(
        0.0,
        float(battery_capacity)
    )

    stored_energy = max(
        0.0,
        min(
            float(stored_energy),
            battery_capacity
        )
    )

    renewable = solar + wind


    # ======================================
    # LOAD TYPES
    # ======================================

    critical_load = (
        load * CRITICAL_PERCENT
    )

    important_load = (
        load * IMPORTANT_PERCENT
    )

    flexible_load = (
        load * FLEXIBLE_PERCENT
    )


    # ======================================
    # INITIAL VALUES
    # ======================================

    renewable_to_load = 0.0

    battery_charged = 0.0
    battery_used = 0.0

    generator = 0.0
    curtailed = 0.0

    flexible_reduction = 0.0


    # ======================================
    # CURRENT SOC
    # ======================================

    if battery_capacity > 0:

        soc = (
            stored_energy /
            battery_capacity
        ) * 100.0

    else:

        soc = 0.0


    # ======================================
    # SIMPLE LOGIC
    # ======================================

    # --------------------------------------
    # CASE 1:
    # Renewable is enough for total load
    # --------------------------------------

    if renewable >= load:

        # Renewable supplies complete load

        renewable_to_load = load

        remaining_renewable = (
            renewable - load
        )


        # Flexible load is NOT reduced
        flexible_reduction = 0.0


        # ----------------------------------
        # Excess renewable → Battery
        # ----------------------------------

        if battery_capacity > 0:

            battery_space = max(
                0.0,
                battery_capacity -
                stored_energy
            )

            energy_to_battery = min(
                remaining_renewable *
                CHARGE_EFFICIENCY,
                battery_space
            )

            stored_energy += (
                energy_to_battery
            )

            battery_charged = (
                energy_to_battery
            )


            if energy_to_battery > 0:

                renewable_used = (
                    energy_to_battery /
                    CHARGE_EFFICIENCY
                )

            else:

                renewable_used = 0.0


            curtailed = max(
                0.0,
                remaining_renewable -
                renewable_used
            )

        else:

            curtailed = (
                remaining_renewable
            )


    # --------------------------------------
    # CASE 2:
    # Renewable is NOT enough
    # --------------------------------------

    else:

        # Renewable supplies whatever
        # it can

        renewable_to_load = renewable

        remaining_load = (
            load -
            renewable_to_load
        )


        # ----------------------------------
        # Flexible load reduction
        # based on battery SOC
        # ----------------------------------

        reduction_percent = (
            get_flexible_reduction(soc)
        )


        flexible_reduction = min(
            flexible_load *
            reduction_percent,
            remaining_load
        )


        # Reduce remaining load

        remaining_load -= (
            flexible_reduction
        )


        # ----------------------------------
        # Battery supplies remaining load
        # ----------------------------------

        if (
            remaining_load > 0
            and battery_capacity > 0
        ):

            minimum_energy = (
                battery_capacity *
                MIN_SOC /
                100.0
            )

            available_battery = max(
                0.0,
                stored_energy -
                minimum_energy
            )


            battery_required = (
                remaining_load /
                DISCHARGE_EFFICIENCY
            )


            battery_output = min(
                battery_required,
                available_battery
            )


            # Remove from battery

            stored_energy -= (
                battery_output
            )


            # Actual load supplied

            battery_used = (
                battery_output *
                DISCHARGE_EFFICIENCY
            )


            remaining_load -= (
                battery_used
            )


        # ----------------------------------
        # Generator backup
        # ----------------------------------

        if remaining_load > 0:

            generator = (
                remaining_load
            )

            remaining_load = 0.0


    # ======================================
    # FINAL SOC
    # ======================================

    if battery_capacity > 0:

        new_soc = (
            stored_energy /
            battery_capacity
        ) * 100.0

    else:

        new_soc = 0.0


    new_soc = max(
        MIN_SOC
        if battery_capacity > 0
        else 0.0,

        min(
            MAX_SOC,
            new_soc
        )
    )


    # ======================================
    # OPTIMIZED LOAD
    # ======================================

    optimized_load = max(
        0.0,
        load -
        flexible_reduction
    )


    # ======================================
    # ACTION
    # ======================================

    if battery_charged > 0:

        action = (
            "Renewable -> Load -> Battery"
        )

    elif flexible_reduction > 0:

        if battery_used > 0:

            action = (
                "Renewable -> "
                "Flexible Reduction -> "
                "Battery"
            )

        elif generator > 0:

            action = (
                "Renewable -> "
                "Flexible Reduction -> "
                "Generator"
            )

        else:

            action = (
                "Renewable -> "
                "Flexible Reduction"
            )

    elif battery_used > 0:

        action = (
            "Renewable -> Battery -> Load"
        )

    elif generator > 0:

        action = (
            "Renewable -> Generator"
        )

    else:

        action = (
            "Renewable -> Load"
        )


    # ======================================
    # RETURN
    # ======================================

    return {

        "renewable":
            renewable,

        "critical_load":
            critical_load,

        "important_load":
            important_load,

        "flexible_load":
            flexible_load,

        "critical_supplied":
            critical_load
            if renewable >= critical_load
            else renewable,

        "important_supplied":
            0.0,

        "flexible_supplied":
            0.0,

        "renewable_to_load":
            renewable_to_load,

        "flexible_reduction":
            flexible_reduction,

        "optimized_load":
            optimized_load,

        "battery_charged":
            battery_charged,

        "battery_used":
            battery_used,

        "stored_energy":
            stored_energy,

        "soc":
            new_soc,

        "generator":
            generator,

        "curtailed":
            curtailed,

        "action":
            action
    }