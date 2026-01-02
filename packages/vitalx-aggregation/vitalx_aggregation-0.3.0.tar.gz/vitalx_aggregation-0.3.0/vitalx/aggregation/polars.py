import polars
import polars._typing

from vitalx.types.query import (
    ActivityColumnT,
    BodyColumnT,
    MealColumnT,
    ProfileColumnT,
    SleepColumnT,
    TimeseriesFieldsT,
    WorkoutColumnT,
)

PolarsNaiveDatetime = polars.Datetime(time_zone=None, time_unit="ms")
PolarsUTCDatetime = polars.Datetime(time_zone="UTC", time_unit="ms")

CategoricalSexAndGender = polars.Categorical(polars.Categories(name="sex_and_gender"))
CategoricalSourceProvider = polars.Categorical(
    polars.Categories(name="source_provider")
)
CategoricalSourceType = polars.Categorical(polars.Categories(name="source_type"))
CategoricalSourceAppID = polars.Categorical(polars.Categories(name="source_app_id"))
CategoricalSourceDeviceID = polars.Categorical(
    polars.Categories(name="source_device_id")
)

DF_GROUP_KEY = "group_key"

SLEEP_DATAFRAME_SCHEMA: dict[SleepColumnT, polars._typing.PolarsDataType] = {
    "id": polars.Utf8,
    "session_start": polars.Datetime(time_zone=None, time_unit="ms"),
    "session_end": polars.Datetime(time_zone=None, time_unit="ms"),
    "state": polars.Utf8,
    "duration_second": polars.Int64,
    "stage_asleep_second": polars.Int64,
    "stage_awake_second": polars.Int64,
    "stage_light_second": polars.Int64,
    "stage_rem_second": polars.Int64,
    "stage_deep_second": polars.Int64,
    "stage_unknown_second": polars.Int64,
    "latency_second": polars.Int64,
    "heart_rate_minimum": polars.Int64,
    "heart_rate_mean": polars.Int64,
    "heart_rate_maximum": polars.Int64,
    "heart_rate_resting": polars.Int64,
    "heart_rate_dip": polars.Float64,
    "efficiency": polars.Float64,
    "hrv_mean_rmssd": polars.Float64,
    "hrv_mean_sdnn": polars.Float64,
    "skin_temperature_delta": polars.Float64,
    "respiratory_rate": polars.Float64,
    "score": polars.Int64,
    "source_type": polars.Utf8,
    "type": polars.Utf8,
    "source_provider": polars.Utf8,
    "source_app_id": polars.Utf8,
}

ACTIVITY_DATAFRAME_SCHEMA: dict[ActivityColumnT, polars._typing.PolarsDataType] = {
    "date": polars.Date(),
    "calories_total": polars.Float64,
    "calories_active": polars.Float64,
    "steps": polars.Int64,
    "distance_meter": polars.Float64,
    "floors_climbed": polars.Int64,
    "duration_active_second": polars.Int64,
    "intensity_sedentary_second": polars.Int64,
    "intensity_low_second": polars.Int64,
    "intensity_medium_second": polars.Int64,
    "intensity_high_second": polars.Int64,
    "heart_rate_mean": polars.Float64,
    "heart_rate_minimum": polars.Float64,
    "heart_rate_maximum": polars.Float64,
    "heart_rate_resting": polars.Float64,
    "heart_rate_mean_walking": polars.Float64,
    "wheelchair_use": polars.Boolean,
    "wheelchair_push": polars.Int64,
    "source_type": polars.Utf8,
    "source_provider": polars.Utf8,
    "source_app_id": polars.Utf8,
}

WORKOUT_DATAFRAME_SCHEMA: dict[WorkoutColumnT, polars._typing.PolarsDataType] = {
    "session_start": polars.Datetime(time_zone=None, time_unit="ms"),
    "session_end": polars.Datetime(time_zone=None, time_unit="ms"),
    "title": polars.Utf8,
    "sport_name": polars.Utf8,
    "sport_slug": polars.Utf8,
    "duration_active_second": polars.Int64,
    "heart_rate_mean": polars.Int64,
    "heart_rate_minimum": polars.Int64,
    "heart_rate_maximum": polars.Int64,
    "heart_rate_zone_1": polars.Float64,
    "heart_rate_zone_2": polars.Float64,
    "heart_rate_zone_3": polars.Float64,
    "heart_rate_zone_4": polars.Float64,
    "heart_rate_zone_5": polars.Float64,
    "heart_rate_zone_6": polars.Float64,
    "distance_meter": polars.Float64,
    "calories": polars.Float64,
    "elevation_gain_meter": polars.Float64,
    "elevation_maximum_meter": polars.Float64,
    "elevation_minimum_meter": polars.Float64,
    "speed_mean": polars.Float64,
    "speed_maximum": polars.Float64,
    "power_source": polars.Utf8,
    "power_mean": polars.Float64,
    "power_maximum": polars.Float64,
    "power_weighted_mean": polars.Float64,
    "steps": polars.Int64,
    "map_polyline": polars.Utf8,
    "map_summary_polyline": polars.Utf8,
    "source_type": polars.Utf8,
    "source_provider": polars.Utf8,
    "source_app_id": polars.Utf8,
}


BODY_DATAFRAME_SCHEMA: dict[BodyColumnT, polars._typing.PolarsDataType] = {
    "measured_at": polars.Datetime(time_zone=None, time_unit="ms"),
    "weight_kilogram": polars.Float64,
    "fat_mass_percentage": polars.Float64,
    "water_percentage": polars.Float64,
    "muscle_mass_percentage": polars.Float64,
    "visceral_fat_index": polars.Float64,
    "bone_mass_percentage": polars.Float64,
    "lean_body_mass_kilogram": polars.Float64,
    "body_mass_index": polars.Float64,
    "waist_circumference_centimeter": polars.Float64,
    "source_type": polars.Utf8,
    "source_provider": polars.Utf8,
    "source_app_id": polars.Utf8,
}

MEAL_DATAFRAME_SCHEMA: dict[MealColumnT, polars._typing.PolarsDataType] = {
    # Common
    "date": polars.Date,
    "name": polars.Utf8,
    "source_type": polars.Utf8,
    "source_provider": polars.Utf8,
    "source_app_id": polars.Utf8,
    # Nutritional data
    "calories": polars.Float64,
    # Macros
    "carbohydrate_gram": polars.Float64,
    "protein_gram": polars.Float64,
    "alcohol_gram": polars.Float64,
    "fibre_gram": polars.Float64,
    "sugar_gram": polars.Float64,
    "cholesterol_gram": polars.Float64,
    # Fats
    "saturated_fat_gram": polars.Float64,
    "monounsaturated_fat_gram": polars.Float64,
    "polyunsaturated_fat_gram": polars.Float64,
    "omega3_fat_gram": polars.Float64,
    "omega6_fat_gram": polars.Float64,
    "total_fat_gram": polars.Float64,
    # Minerals
    "sodium_milligram": polars.Float64,
    "potassium_milligram": polars.Float64,
    "calcium_milligram": polars.Float64,
    "phosphorus_milligram": polars.Float64,
    "magnesium_milligram": polars.Float64,
    "iron_milligram": polars.Float64,
    "zinc_milligram": polars.Float64,
    "fluoride_milligram": polars.Float64,
    "chloride_milligram": polars.Float64,
    # Vitamins
    "vitamin_a_milligram": polars.Float64,
    "vitamin_b1_milligram": polars.Float64,
    "riboflavin_milligram": polars.Float64,
    "niacin_milligram": polars.Float64,
    "pantothenic_acid_milligram": polars.Float64,
    "vitamin_b6_milligram": polars.Float64,
    "biotin_microgram": polars.Float64,
    "vitamin_b12_microgram": polars.Float64,
    "vitamin_c_milligram": polars.Float64,
    "vitamin_d_microgram": polars.Float64,
    "vitamin_e_milligram": polars.Float64,
    "vitamin_k_microgram": polars.Float64,
    "folic_acid_microgram": polars.Float64,
    # Trace Elements
    "chromium_microgram": polars.Float64,
    "copper_milligram": polars.Float64,
    "iodine_microgram": polars.Float64,
    "manganese_milligram": polars.Float64,
    "molybdenum_microgram": polars.Float64,
    "selenium_microgram": polars.Float64,
}

PROFILE_DATAFRAME_SCHEMA: dict[ProfileColumnT, polars._typing.PolarsDataType] = {
    "height_centimeter": polars.Int16,
    "birth_date": polars.Date,
    "wheelchair_use": polars.Boolean,
    "gender": CategoricalSexAndGender,
    "sex": CategoricalSexAndGender,
    "source_type": CategoricalSourceType,
    "source_provider": CategoricalSourceProvider,
    "source_app_id": CategoricalSourceAppID,
    "source_device_id": CategoricalSourceDeviceID,
    "created_at": PolarsUTCDatetime,
    "updated_at": PolarsUTCDatetime,
}

TIMESERIES_DATAFRAME_SCHEMA: dict[TimeseriesFieldsT, polars._typing.PolarsDataType] = {
    # Common columns
    "source_provider": polars.Utf8,
    "source_type": polars.Utf8,
    "source_workout_id": polars.Utf8,
    "source_sport": polars.Utf8,
    "timezone_offset": polars.Int64,
    # Common but as fields
    "value": polars.Float64,
    "type": polars.Utf8,
    # Subtype specific fields
    # Blood Pressure
    "diastolic": polars.Float64,
    "systolic": polars.Float64,
    # Temperature,
    "sensor_location": polars.Utf8,
    # Workout duration
    "intensity": polars.Utf8,
    # Note
    "tags": polars.List(polars.Utf8),
    "content": polars.Utf8,
}
