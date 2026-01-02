from typing import Annotated, Literal, Self, Sequence

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from vitalx.types.providers import Labs, Providers

DateTimeUnit = Literal["minute", "hour", "day", "week", "month", "year"]


class Placeholder(BaseModel):
    placeholder: Literal[True]


class Period(BaseModel):
    value: Annotated[int, Field(ge=1)] = 1
    unit: DateTimeUnit

    @model_validator(mode="after")
    def validate_value(self) -> Self:
        if self.unit == "month" and 12 % self.value != 0:
            raise ValueError(
                "your DateTrunc period must divide 12 months without remainder."
            )
        return self


# Select Expressions

TableT = Literal[
    "sleep", "activity", "workout", "body", "meal", "profile", "timeseries"
]

SleepColumnT = Literal[
    "id",
    "session_start",
    "session_end",
    "state",
    "type",
    "duration_second",
    "stage_asleep_second",
    "stage_awake_second",
    "stage_light_second",
    "stage_rem_second",
    "stage_deep_second",
    "stage_unknown_second",
    "latency_second",
    "heart_rate_minimum",
    "heart_rate_mean",
    "heart_rate_maximum",
    "heart_rate_dip",
    "heart_rate_resting",
    "efficiency",
    "hrv_mean_rmssd",
    "hrv_mean_sdnn",
    "skin_temperature",
    "skin_temperature_delta",
    "respiratory_rate",
    "score",
    "source_type",
    "source_provider",
    "source_app_id",
    "source_device_id",
    "time_zone",
]


ActivityColumnT = Literal[
    "date",
    "calories_total",
    "calories_active",
    "steps",
    "distance_meter",
    "floors_climbed",
    "duration_active_second",
    "intensity_sedentary_second",
    "intensity_low_second",
    "intensity_medium_second",
    "intensity_high_second",
    "heart_rate_mean",
    "heart_rate_minimum",
    "heart_rate_maximum",
    "heart_rate_resting",
    "heart_rate_mean_walking",
    "wheelchair_use",
    "wheelchair_push",
    "source_type",
    "source_provider",
    "source_app_id",
    "source_device_id",
    "time_zone",
    "time_zone_offset",
]

WorkoutColumnT = Literal[
    "session_start",
    "session_end",
    "title",
    "sport_name",
    "sport_slug",
    "duration_active_second",
    "heart_rate_mean",
    "heart_rate_minimum",
    "heart_rate_maximum",
    "heart_rate_zone_1",
    "heart_rate_zone_2",
    "heart_rate_zone_3",
    "heart_rate_zone_4",
    "heart_rate_zone_5",
    "heart_rate_zone_6",
    "distance_meter",
    "calories",
    "elevation_gain_meter",
    "elevation_maximum_meter",
    "elevation_minimum_meter",
    "speed_mean",
    "speed_maximum",
    "power_source",
    "power_mean",
    "power_maximum",
    "power_weighted_mean",
    "steps",
    "map_polyline",
    "map_summary_polyline",
    "source_type",
    "source_provider",
    "source_app_id",
    "source_device_id",
    "external_id",
    "time_zone",
]

BodyColumnT = Literal[
    "measured_at",
    "weight_kilogram",
    "fat_mass_percentage",
    "water_percentage",
    "muscle_mass_percentage",
    "visceral_fat_index",
    "bone_mass_percentage",
    "body_mass_index",
    "lean_body_mass_kilogram",
    "waist_circumference_centimeter",
    "source_type",
    "source_provider",
    "source_app_id",
    "source_device_id",
    "time_zone",
]

MealColumnT = Literal[
    "calories",
    # Macros
    "carbohydrate_gram",
    "protein_gram",
    "alcohol_gram",
    "water_gram",
    "fibre_gram",
    "sugar_gram",
    "cholesterol_gram",
    # Fats
    "saturated_fat_gram",
    "monounsaturated_fat_gram",
    "polyunsaturated_fat_gram",
    "omega3_fat_gram",
    "omega6_fat_gram",
    "total_fat_gram",
    # Minerals
    "sodium_milligram",
    "potassium_milligram",
    "calcium_milligram",
    "phosphorus_milligram",
    "magnesium_milligram",
    "iron_milligram",
    "zinc_milligram",
    "fluoride_milligram",
    "chloride_milligram",
    # Vitamins
    "vitamin_a_milligram",
    "vitamin_b1_milligram",
    "riboflavin_milligram",
    "niacin_milligram",
    "pantothenic_acid_milligram",
    "vitamin_b6_milligram",
    "biotin_microgram",
    "vitamin_b12_microgram",
    "vitamin_c_milligram",
    "vitamin_d_microgram",
    "vitamin_e_milligram",
    "vitamin_k_microgram",
    "folic_acid_microgram",
    # Trace Elements
    "chromium_microgram",
    "copper_milligram",
    "iodine_microgram",
    "manganese_milligram",
    "molybdenum_microgram",
    "selenium_microgram",
    "date",
    "name",
    "source_type",
    "source_provider",
    "source_app_id",
    "source_device_id",
]

ProfileColumnT = Literal[
    "height_centimeter",
    "birth_date",
    "wheelchair_use",
    "gender",
    "sex",
    "source_type",
    "source_provider",
    "source_app_id",
    "source_device_id",
    "created_at",
    "updated_at",
]

AggregateFunctionT = Literal[
    "mean", "min", "max", "sum", "count", "median", "stddev", "oldest", "newest"
]

DiscreteTimeseriesT = Literal[
    "glucose",
    "heartrate",
    "hrv",
    "ige",
    "igg",
    "cholesterol",
    "weight",
    "fat",
    "blood_oxygen",
    "electrocardiogram_voltage",
    "respiratory_rate",
    "stress_level",
]

IntervalTimeseriesT = Literal[
    "steps",
    "distance",
    "vo2_max",
    "heart_rate_alert",
    "stand_hour",
    "sleep_breathing_disturbance",
    "insulin_injection",
    "water",
    "caffeine",
    "mindfulness_minutes",
    "steps",
    "calories_active",
    "distance",
    "floors_climbed",
    "vo2_max",
    "calories_basal",
    "afib_burden",
    "stand_hour",
    "stand_duration",
    "sleep_apnea_alert",
    "sleep_breathing_disturbance",
    "wheelchair_push",
    "forced_expiratory_volume_1",
    "forced_vital_capacity",
    "peak_expiratory_flow_rate",
    "inhaler_usage",
    "fall",
    "uv_exposure",
    "daylight_exposure",
    "handwashing",
    "basal_body_temperature",
    "body_mass_index",
    "lean_body_mass",
    "waist_circumference",
    "heart_rate_recovery_one_minute",
    "workout_swimming_stroke",
    "workout_distance",
    "carbohydrates",
    "insulin_injection",
]

BloodPressureTimeseriesT = Literal["blood_pressure"]

WorkoutDurationTimeseriesT = Literal["workout_duration"]

TemperatureTimeseriesT = Literal["body_temperature", "body_temperature_delta"]

NoteTimeseriesT = Literal["note"]

TimeseriesT = (
    DiscreteTimeseriesT
    | IntervalTimeseriesT
    | BloodPressureTimeseriesT
    | TemperatureTimeseriesT
    | WorkoutDurationTimeseriesT
    | NoteTimeseriesT
)

CommonSourceFieldT = Literal[
    "source_provider",
    "source_type",
]

SummarySourceFieldT = CommonSourceFieldT | Literal["source_app_id"]

TimeseriesSourceFieldT = (
    CommonSourceFieldT | Literal["source_workout_id", "source_sport"]
)

SourceFieldT = SummarySourceFieldT | TimeseriesSourceFieldT


CommonFieldsT = (
    SourceFieldT
    | Literal[
        "timezone_offset",
        "type",
    ]
)

DiscreteTimeseriesFieldT = CommonFieldsT | Literal["value"]

IntervalTimeseriesFieldT = CommonFieldsT | Literal["duration", "value"]

BloodPressureTimeseriesFieldT = (
    CommonFieldsT
    | Literal[
        "systolic",
        "diastolic",
    ]
)

NoteTimeseriesFieldT = CommonFieldsT | Literal["tags", "content"]

TemperatureTimeseriesFieldT = IntervalTimeseriesFieldT | Literal["sensor_location"]

WorkoutDurationTimeseriesFieldT = (
    IntervalTimeseriesFieldT
    | Literal[
        "intensity",
    ]
)


class DiscreteTimeseriesExpr(BaseModel):
    timeseries: DiscreteTimeseriesT
    field: DiscreteTimeseriesFieldT

    model_config = ConfigDict(frozen=True)


class IntervalTimeseriesExpr(BaseModel):
    timeseries: IntervalTimeseriesT
    field: IntervalTimeseriesFieldT

    model_config = ConfigDict(frozen=True)


class BloodPressureTimeseriesExpr(BaseModel):
    timeseries: BloodPressureTimeseriesT
    field: BloodPressureTimeseriesFieldT

    model_config = ConfigDict(frozen=True)


class TemperatureTimeseriesExpr(BaseModel):
    timeseries: TemperatureTimeseriesT
    field: TemperatureTimeseriesFieldT

    model_config = ConfigDict(frozen=True)


class WorkoutDurationTimeseriesExpr(BaseModel):
    timeseries: WorkoutDurationTimeseriesT
    field: WorkoutDurationTimeseriesFieldT

    model_config = ConfigDict(frozen=True)


class NoteTimeseriesExpr(BaseModel):
    timeseries: NoteTimeseriesT
    field: NoteTimeseriesFieldT

    model_config = ConfigDict(frozen=True)


TimeseriesFieldsT = (
    DiscreteTimeseriesFieldT
    | IntervalTimeseriesFieldT
    | BloodPressureTimeseriesFieldT
    | TemperatureTimeseriesFieldT
    | WorkoutDurationTimeseriesFieldT
    | NoteTimeseriesFieldT
)

TimeseriesExpr = (
    DiscreteTimeseriesExpr
    | IntervalTimeseriesExpr
    | BloodPressureTimeseriesExpr
    | TemperatureTimeseriesExpr
    | WorkoutDurationTimeseriesExpr
    | NoteTimeseriesExpr
)


class TimeseriesMagicExpr(BaseModel):
    timeseries: TimeseriesExpr | TimeseriesSourceFieldT | Literal["index"]

    model_config = ConfigDict(frozen=True)


class SleepColumnExpr(BaseModel):
    sleep: SleepColumnT

    model_config = ConfigDict(frozen=True)


class ActivityColumnExpr(BaseModel):
    activity: ActivityColumnT

    model_config = ConfigDict(frozen=True)


class WorkoutColumnExpr(BaseModel):
    workout: WorkoutColumnT

    model_config = ConfigDict(frozen=True)


class BodyColumnExpr(BaseModel):
    body: BodyColumnT

    model_config = ConfigDict(frozen=True)


class MealColumnExpr(BaseModel):
    meal: MealColumnT

    model_config = ConfigDict(frozen=True)


class ProfileColumnExpr(BaseModel):
    profile: ProfileColumnT

    model_config = ConfigDict(frozen=True)


class IndexColumnExpr(BaseModel):
    index: TableT


class GroupKeyColumnExpr(BaseModel):
    group_key: int | Literal["*"]


class SleepScoreValueMacroExpr(BaseModel):
    value_macro: Literal["sleep_score"]
    version: Literal["automatic"] = "automatic"


class ChronotypeValueMacroExpr(BaseModel):
    value_macro: Literal["chronotype"]
    version: Literal["automatic"] = "automatic"


class AsleepAtValueMacroExpr(BaseModel):
    value_macro: Literal["asleep_at"]
    version: Literal["automatic"] = "automatic"


class AwakeAtValueMacroExpr(BaseModel):
    value_macro: Literal["awake_at"]
    version: Literal["automatic"] = "automatic"


class UnrecognizedValueMacroExpr(BaseModel):
    value_macro: str


ValueMacroExpr = (
    SleepScoreValueMacroExpr
    | ChronotypeValueMacroExpr
    | AsleepAtValueMacroExpr
    | AwakeAtValueMacroExpr
    | UnrecognizedValueMacroExpr
)

DataColumnExpr = (
    SleepColumnExpr
    | ActivityColumnExpr
    | WorkoutColumnExpr
    | BodyColumnExpr
    | MealColumnExpr
    | ProfileColumnExpr
    | ValueMacroExpr
    | TimeseriesExpr
)

ColumnExpr = DataColumnExpr | IndexColumnExpr


class SourceColumnExpr(BaseModel):
    source: SourceFieldT


class AggregateExpr(BaseModel):
    arg: ColumnExpr
    func: AggregateFunctionT


SelectExpr = AggregateExpr | GroupKeyColumnExpr | ColumnExpr | SourceColumnExpr

# Partitioning and Swizzling

DatePartT = DateTimeUnit | Literal["weekday", "week_of_year", "day_of_year"]


class DateTruncExpr(BaseModel):
    date_trunc: Period
    arg: IndexColumnExpr | Placeholder


class DatePartExpr(BaseModel):
    arg: IndexColumnExpr | Placeholder
    date_part: DatePartT


GroupByExpr = DateTruncExpr | DatePartExpr | DataColumnExpr | SourceColumnExpr

# Query


class Query(BaseModel):
    select: Sequence[SelectExpr]
    group_by: list[GroupByExpr] = Field(default_factory=list)

    where: str | None = None
    """
    A WHERE clause filtering the input data. If a GROUP BY clause is present, filtering happens prior to GROUP BY evaluation.

    WHERE clause uses SQL Expression syntax to describe the filtering criteria:
    * Available operators: `>`, `>=`, `<`, `<=`, `=`, `!=`, `NOT`, `AND` and `OR`.
    * Parentheses is supported.
    """

    model_config = ConfigDict(use_attribute_docstrings=True)

    @field_validator("group_by", mode="after")
    @classmethod
    def validate_group_by(cls, v: list[GroupByExpr]) -> list[GroupByExpr]:
        date_trunc_count = sum(isinstance(expr, DateTruncExpr) for expr in v)
        if date_trunc_count >= 2:
            raise ValueError(
                f"group_by supports at most 1 DateTruncExpr. found {date_trunc_count}."
            )
        return v

    @model_validator(mode="after")
    def validate_aggregate_expr_present(self, v) -> Self:

        if self.group_by:
            # All select expressions must be AggregateExpr or GroupKeyColumnExpr
            # in a GroupBy context.
            if any(
                not isinstance(expr, (AggregateExpr, GroupKeyColumnExpr))
                for expr in self.select
            ):
                raise ValueError(
                    "Select expressions must either be AggregateExpr or GroupKeyColumnExpr in a GroupBy context."
                )

        return self


class QueryConfig(BaseModel):
    provider_priority_overrides: list[Providers | Labs] | None = None
