from typing import Dict, Any, Optional, List

class DeterministicHazardRiskEngine:
    """
    Evaluates meteorological indicators, forecast trends, and official warning presence
    to calculate a transparent, deterministic hazard risk score between 0 and 100.
    """

    def compute_risk(
        self,
        forecast_daily: List[Any],
        forecast_hourly: List[Any],
        current_weather: Optional[Any],
        has_official_warning: bool,
        official_warning_severity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates normalized hazard risk metrics.
        """
        rainfall_risk = 0.0
        wind_risk = 0.0
        storm_risk = 0.0
        temp_risk = 0.0
        official_weight = 0.0

        reasons = []

        # 1. Rainfall Risk (Max 35 points)
        # Check next 24-48 hours precipitation
        max_24h_precip = 0.0
        max_rain_prob = 0
        if forecast_daily and len(forecast_daily) > 0:
            max_24h_precip = max(d.precipitation for d in forecast_daily[:2])
            max_rain_prob = max(d.rain_probability for d in forecast_daily[:2])

        if max_24h_precip >= 115.5:  # Extremely Heavy Rain (IMD)
            rainfall_risk = 35.0
            reasons.append(f"Extremely heavy rainfall forecast ({max_24h_precip} mm/24h)")
        elif max_24h_precip >= 64.5:  # Heavy Rain (IMD)
            rainfall_risk = 28.0
            reasons.append(f"Heavy rainfall accumulation forecast ({max_24h_precip} mm/24h)")
        elif max_24h_precip >= 35.0:  # Moderate-Heavy Rain
            rainfall_risk = 18.0
            reasons.append(f"Moderate to heavy rainfall expected ({max_24h_precip} mm)")
        elif max_24h_precip >= 15.0:
            rainfall_risk = 10.0
            reasons.append(f"Light to moderate rainfall expected ({max_24h_precip} mm)")
        elif max_rain_prob >= 70:
            rainfall_risk = 6.0
            reasons.append(f"High precipitation probability ({max_rain_prob}%)")

        # 2. Wind & Gust Risk (Max 25 points)
        curr_wind = current_weather.wind_speed if current_weather else 0.0
        max_daily_wind = max((d.wind_speed_max for d in forecast_daily[:2]), default=0.0) if forecast_daily else 0.0
        effective_wind = max(curr_wind, max_daily_wind)

        if effective_wind >= 75.0:  # Violent storm / Cyclone gale
            wind_risk = 25.0
            reasons.append(f"Severe gale/squall winds forecast ({effective_wind} km/h)")
        elif effective_wind >= 55.0:  # Strong gale
            wind_risk = 20.0
            reasons.append(f"Squally strong winds forecast ({effective_wind} km/h)")
        elif effective_wind >= 40.0:  # Moderate gale
            wind_risk = 12.0
            reasons.append(f"Elevated wind speeds ({effective_wind} km/h)")
        elif effective_wind >= 25.0:
            wind_risk = 5.0

        # 3. Convective Storm & Lightning Risk (Max 20 points)
        curr_code = current_weather.condition_code if current_weather else 0
        hourly_storm_codes = [h.condition_code for h in forecast_hourly[:12]] if forecast_hourly else []

        if curr_code in [96, 99] or any(c in [96, 99] for c in hourly_storm_codes):
            storm_risk = 20.0
            reasons.append("Severe thunderstorm with hail and heavy lightning activity detected")
        elif curr_code == 95 or any(c == 95 for c in hourly_storm_codes):
            storm_risk = 15.0
            reasons.append("Convective thunderstorm activity expected within the next 12 hours")
        elif curr_code in [80, 81, 82] or any(c in [80, 81, 82] for c in hourly_storm_codes):
            storm_risk = 8.0
            reasons.append("Atmospheric instability with sharp convective showers")

        # 4. Temperature Extremes Risk (Heat Wave / Cold Wave) (Max 15 points)
        max_temp = max((d.temp_max for d in forecast_daily[:2]), default=30.0) if forecast_daily else 30.0
        min_temp = min((d.temp_min for d in forecast_daily[:2]), default=20.0) if forecast_daily else 20.0

        if max_temp >= 44.0:
            temp_risk = 15.0
            reasons.append(f"Severe heatwave conditions with peak temperature of {max_temp}°C")
        elif max_temp >= 40.0:
            temp_risk = 10.0
            reasons.append(f"Heatwave criteria met with maximum temperature of {max_temp}°C")
        elif min_temp <= 4.0:
            temp_risk = 12.0
            reasons.append(f"Severe cold wave condition with minimum temperature of {min_temp}°C")
        elif min_temp <= 8.0:
            temp_risk = 6.0
            reasons.append(f"Cold wave conditions with minimum temperature of {min_temp}°C")

        # 5. Official Warning Weight (Max 25 points boost)
        if has_official_warning:
            if official_warning_severity == "Emergency" or official_warning_severity == "Red":
                official_weight = 25.0
            elif official_warning_severity == "Warning" or official_warning_severity == "Orange":
                official_weight = 20.0
            else:
                official_weight = 12.0
            reasons.append("Active official government warning in effect")

        # Sum and clamp to 0-100
        total_score = min(100.0, rainfall_risk + wind_risk + storm_risk + temp_risk + official_weight)
        int_score = int(round(total_score))

        # Categorize Level
        if int_score >= 90:
            level = "EXTREME"
        elif int_score >= 75:
            level = "VERY HIGH"
        elif int_score >= 55:
            level = "HIGH"
        elif int_score >= 25:
            level = "MODERATE"
        else:
            level = "LOW"

        # Confidence Calculation
        if has_official_warning and (rainfall_risk > 15 or storm_risk > 10 or wind_risk > 10):
            confidence = "High"
        elif rainfall_risk > 15 or storm_risk > 10 or wind_risk > 15 or temp_risk > 8:
            confidence = "Moderate"
        else:
            confidence = "Low"

        # Expected Window
        if curr_code in [95, 96, 99] or curr_wind >= 40:
            expected_window = "Immediate – Next 3–6 hours"
        elif rainfall_risk >= 18 or storm_risk >= 12:
            expected_window = "Next 6–12 hours"
        elif int_score >= 25:
            expected_window = "Next 12–24 hours"
        else:
            expected_window = "Next 24–48 hours (Seasonal Outlook)"

        final_reason = "; ".join(reasons) if reasons else "Meteorological observations and forecast variables remain within standard seasonal thresholds."

        return {
            "score": int_score,
            "level": level,
            "confidence": confidence,
            "expected_window": expected_window,
            "reason": final_reason,
            "hazard_breakdown": {
                "rainfall": round(rainfall_risk, 1),
                "wind": round(wind_risk, 1),
                "storm": round(storm_risk, 1),
                "temperature": round(temp_risk, 1),
                "official_warning_boost": round(official_weight, 1)
            },
            "disclaimer": "AI risk assessment is an analytical estimate based on available forecast and hazard data. It is not an official disaster warning. Follow official authorities for emergency instructions."
        }

hazard_risk_engine = DeterministicHazardRiskEngine()
