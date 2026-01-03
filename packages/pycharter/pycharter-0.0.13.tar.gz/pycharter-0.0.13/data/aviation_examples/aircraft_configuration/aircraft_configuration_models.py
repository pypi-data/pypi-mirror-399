from datetime import datetime
from typing import Optional, List
import logging

from pydantic import Field, BaseModel

logger = logging.getLogger(__name__)


class AircraftCompartment(BaseModel):
    """Aircraft compartment configuration with seat details"""

    curtain_version: str = Field(
        ...,
        description="Position the movable cabin divider",
    )
    compartment: str = Field(
        ...,
        description="Compartment code",
    )
    valid_since: datetime = Field(
        ...,
        description="Start of validity",
    )
    valid_until: datetime = Field(
        ...,
        description="End of validity",
    )
    seats: Optional[int] = Field(
        None,
        description="Available seats",
    )
    # Flattened compartment details from compartment lookup
    code: str = Field(
        ...,
        description="Compartment identifier (e.g. F/C/Y)",
    )
    priority: int = Field(
        ...,
        description="Compartments are ordered by priority",
    )
    name: Optional[str] = Field(
        None,
        description="Long Name of Compartment",
    )
    booking_classes: Optional[str] = Field(
        None,
        description="Booking Class Codes, not separated",
    )
    three_comp_code: str = Field(
        ...,
        description="only F, C or Y allowed",
    )


class AircraftRestriction(BaseModel):
    """Aircraft restriction with associated constraint codes"""

    r_no: int = Field(
        ...,
        description="Restriction number",
    )
    update_no: int = Field(
        ...,
        description="Update transaction reference",
    )
    restr_type: str = Field(
        ...,
        description="Restriction type: A/T/P/B/Y",
    )
    mark: str = Field(
        ...,
        description="Restriction should be marked ('Y'/'N') in aircraft label",
    )
    technical_reason: Optional[str] = Field(
        None,
        description="Technical Reason",
    )
    workorder_no: Optional[int] = Field(
        None,
        description="Reference to M+E workorder",
    )
    remark: Optional[str] = Field(
        None,
        description="Additional remark",
    )
    valid_since: datetime = Field(
        ...,
        description="Start of validity",
    )
    valid_until: datetime = Field(
        ...,
        description="End of Validity",
    )
    expire_date: Optional[datetime] = Field(
        None,
        description="Date when the MEL-Item has to be fixed",
    )
    expire_total_fh_hours: Optional[int] = Field(
        None,
        description="Expiry total flight hours",
    )
    expire_total_fh_minutes: Optional[int] = Field(
        None,
        description="Expiry total flight minutes",
    )
    expire_total_cycles: Optional[int] = Field(
        None,
        description="Expiry total cycles",
    )
    entry_dt: datetime = Field(
        ...,
        description="Timestamp of the last update",
    )
    entry_user: str = Field(
        ...,
        description="Userstamp of the last update",
    )
    # ATA chapter fields (removed via $$REMOVE in pipeline but present in
    # source)
    ata_chapter: Optional[str] = Field(
        None,
        description="ATA chapter code",
    )
    ata_subchapter: Optional[str] = Field(
        None,
        description="ATA subchapter code",
    )
    ata_section: Optional[str] = Field(
        None,
        description="ATA section code",
    )
    ata_item: Optional[str] = Field(
        None,
        description="ATA item code",
    )
    ata_description: Optional[str] = Field(
        None,
        description="Descriptive text as defined by ATA",
    )
    description: Optional[str] = Field(
        None,
        description="Descriptive text for the restriction",
    )
    limitations: Optional[str] = Field(
        None,
        description=(
            "Text describing the effect of the restriction on the "
            "aircraft performance"
        ),
    )
    operating_state: str = Field(
        default="N",
        description=(
            "Determines if ac_restriction is a feature (Y) or a missing "
            "requirement (N)"
        ),
    )
    telex: str = Field(
        default="N",
        description=(
            "Determines if ac_restriction shall be added to a generated "
            "TVG/ACH telex"
        ),
    )
    message: Optional[str] = Field(
        None,
        description="A text that is added to the generated TVG/ACH telex",
    )
    sender_object_id: Optional[str] = Field(
        None,
        description="External ID",
    )
    ack_state: str = Field(
        default="N",
        description="For MEL items: was this MEL acknowledged by a user?",
    )
    ack_date: Optional[datetime] = Field(
        None,
        description="Date of acknowledgment",
    )
    ack_user: Optional[str] = Field(
        None,
        description="User, who acknowledged this MEL",
    )
    constraint_code: List[str] = Field(
        default_factory=list,
        description="List of constraint codes from MEL_TO_CONSTRAINT lookup",
    )


class AircraftConfigurationApi(BaseModel):
    """
    Comprehensive aircraft configuration data model joining aircraft, subfleet,
    IATA fleet type, compartment, and restriction data.
    """

    __version__ = "1.0.0"

    # From Aircraft (base)
    registration: str = Field(
        ...,
        description="Registration of the Aircraft",
    )
    valid_since: datetime = Field(
        ...,
        description="Start of validity",
    )
    valid_until: datetime = Field(
        ...,
        description="End of validity",
    )
    ac_operator: str = Field(
        ...,
        description="Aircraft Operator",
    )
    ac_owner: str = Field(
        ...,
        description="Owner of the aircraft",
    )
    ac_subtype: str = Field(
        ...,
        description="Subtype of the aircraft",
    )
    ac_logical_no: int = Field(
        ...,
        description="Logical number of the Aircraft",
    )
    ac_state: str = Field(
        ...,
        description="Status of Aircraft('R'=real and 'O'=overflow)",
    )
    dry_operating_wgt: int = Field(
        ...,
        description="Dry Operating Weight (kg)",
    )
    max_takeoff_wgt: int = Field(
        ...,
        description="Max Takeoff Weight (kg)",
    )
    cargo_capacity: int = Field(
        ...,
        description="Cargo Capacity (kg)",
    )
    fuel_capacity: int = Field(
        ...,
        description="Fuel Capacity (kg)",
    )
    avg_fuel_consump: int = Field(
        ...,
        description="Average Fuel Consumption (kg per hour)",
    )
    ac_index: int = Field(
        ...,
        description="Aircraft index",
    )
    crewsize_cockpit: int = Field(
        ...,
        description="Number of Cockpit Crewmembers",
    )
    crewsize_cabin: int = Field(
        ...,
        description="Number of Cabin Crewmembers",
    )
    std_version: str = Field(
        ...,
        description="Aircraft Standard Version",
    )
    ap_restriction: str = Field(
        ...,
        description=(
            "Airport Restriction - e.g. Political Reason, " "Performance('Y' or 'N')"
        ),
    )
    ac_owner_name: str = Field(
        ...,
        description="Full Name of Owner",
    )
    ac_subtype_name: str = Field(
        ...,
        description="Full Name of Subtype",
    )
    ac_category: str = Field(
        ...,
        description="SSIM-Category of Aircraft",
    )
    remark: Optional[str] = Field(
        None,
        description="Additional remarks",
    )
    fuel_measure_unit: str = Field(
        ...,
        description="Unit for fuel",
    )
    ac_callsign: Optional[str] = Field(
        None,
        description="Callsign of aircraft",
    )
    radio: Optional[str] = Field(
        None,
        description="Radio type",
    )
    noise: Optional[int] = Field(
        None,
        description="ICAO noise chapter",
    )
    phone: Optional[str] = Field(
        None,
        description="Onboard mobile phone number",
    )
    special_equipment: Optional[str] = Field(
        None,
        description="Special equipment",
    )
    acars: Optional[str] = Field(
        None,
        description="ACARS type",
    )
    alt_reg: Optional[str] = Field(
        None,
        description="Alternate Registration",
    )
    record_id: int = Field(
        default=0,
        description="Record ID",
    )
    last_update: Optional[datetime] = Field(
        None,
        description="Timestamp of last update",
    )
    last_update_user_id: Optional[str] = Field(
        None,
        description="User ID of last update",
    )
    std_version_alt_1: Optional[str] = Field(
        None,
        description="Alternative Aircraft Version 1",
    )
    std_version_alt_2: Optional[str] = Field(
        None,
        description="Alternative Aircraft Version 2",
    )
    std_version_alt_3: Optional[str] = Field(
        None,
        description="Alternative Aircraft Version 3",
    )
    std_version_alt_4: Optional[str] = Field(
        None,
        description="Alternative Aircraft Version 4",
    )
    ils_equipment: str = Field(
        default="I",
        description=(
            "aircraft equipment supporting ILS CAT approaches " "(I, II, IIIa, IIIb)"
        ),
    )
    autoland: str = Field(
        default="N",
        description="Autoland capability indicator",
    )
    homebase: Optional[str] = Field(
        None,
        description="Homebase of the aircraft (IATA CODE)",
    )

    # From Subfleet (merged via $replaceRoot)
    aircraft_owner: Optional[str] = Field(
        None,
        description="Aircraft Owner from subfleet",
    )
    aircraft_subtype: Optional[str] = Field(
        None,
        description="Subtype of the Aircraft from subfleet",
    )
    fleet_print_code: Optional[str] = Field(
        None,
        description="Fleet Print Code",
    )
    rotational_flag: Optional[str] = Field(
        None,
        description="Rotational Flag Y/N (Yes/No)",
    )
    standard_configuration: Optional[str] = Field(
        None,
        description="Standard Configuration AC_VERSION.AC_VERSION",
    )
    payload: Optional[float] = Field(
        None,
        description="Payload",
    )
    mtom: Optional[float] = Field(
        None,
        description="Maximum Take-Off Mass",
    )
    max_range: Optional[float] = Field(
        None,
        description="Maximum Range",
    )
    noise_category: Optional[str] = Field(
        None,
        description="Noise Category",
    )
    average_speed: Optional[float] = Field(
        None,
        description="Average Speed",
    )

    # From IATA Fleet Type (merged via $replaceRoot)
    aircraft_group: Optional[str] = Field(
        None,
        description="Group of the Aircraft",
    )
    icao_code: Optional[str] = Field(
        None,
        description="ICAO Code",
    )
    name: Optional[str] = Field(
        None,
        description="Fleet Type Name",
    )
    body_type: Optional[str] = Field(
        None,
        description="Body Type N/W (Narrow/Wide)",
    )
    category: Optional[str] = Field(
        None,
        description="Category H/J/P/S/T",
    )

    # Nested arrays
    aircraft_compartment: List[AircraftCompartment] = Field(
        default_factory=list,
        description="List of aircraft compartments with seat configurations",
    )
    aircraft_restriction: List[AircraftRestriction] = Field(
        default_factory=list,
        description="List of aircraft restrictions with constraint codes",
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "examples": [
                {
                    "registration": "BLBK",
                    "valid_since": {"$date": "2020-12-01T00:00:00.000Z"},
                    "valid_until": {"$date": "2035-12-31T00:00:00.000Z"},
                    "ac_operator": "CX",
                    "ac_owner": "CX",
                    "ac_subtype": "33P",
                    "ac_logical_no": 11,
                    "ac_state": "R",
                    "dry_operating_wgt": 122018,
                    "max_takeoff_wgt": 217000,
                    "cargo_capacity": 0,
                    "fuel_capacity": 0,
                    "avg_fuel_consump": 0,
                    "ac_index": 55,
                    "crewsize_cockpit": 0,
                    "crewsize_cabin": 0,
                    "std_version": "STN",
                    "ap_restriction": "N",
                    "ac_owner_name": "CATHAY PACIFIC",
                    "ac_subtype_name": "330",
                    "ac_category": "J",
                    "remark": "24J/293Y = 317",
                    "fuel_measure_unit": "kg",
                    "ac_callsign": None,
                    "radio": None,
                    "noise": None,
                    "phone": None,
                    "special_equipment": None,
                    "acars": "S",
                    "alt_reg": None,
                    "record_id": 584852,
                    "last_update": {"$date": "2022-03-02T10:36:43.000Z"},
                    "last_update_user_id": "netline",
                    "std_version_alt_1": None,
                    "std_version_alt_2": None,
                    "std_version_alt_3": None,
                    "std_version_alt_4": None,
                    "ils_equipment": "I",
                    "autoland": "Y",
                    "homebase": None,
                    "aircraft_compartment": [
                        {
                            "curtain_version": "",
                            "compartment": "F",
                            "valid_since": {"$date": "2016-01-01T00:00:00.000Z"},
                            "valid_until": {"$date": "2025-01-01T00:00:00.000Z"},
                            "seats": 0,
                            "code": "F",
                            "priority": 1,
                            "name": "First",
                            "booking_classes": "PFA",
                            "three_comp_code": "F",
                        },
                        {
                            "curtain_version": "",
                            "compartment": "J",
                            "valid_since": {"$date": "2016-01-01T00:00:00.000Z"},
                            "valid_until": {"$date": "2025-01-01T00:00:00.000Z"},
                            "seats": 24,
                            "code": "J",
                            "priority": 2,
                            "name": "Business",
                            "booking_classes": "JCDIZ",
                            "three_comp_code": "C",
                        },
                        {
                            "curtain_version": "",
                            "compartment": "W",
                            "valid_since": {"$date": "2016-01-01T00:00:00.000Z"},
                            "valid_until": {"$date": "2025-01-01T00:00:00.000Z"},
                            "seats": 0,
                            "code": "W",
                            "priority": 3,
                            "name": "Premium Eco",
                            "booking_classes": "W",
                            "three_comp_code": "Y",
                        },
                        {
                            "curtain_version": "",
                            "compartment": "Y",
                            "valid_since": {"$date": "2016-01-01T00:00:00.000Z"},
                            "valid_until": {"$date": "2025-01-01T00:00:00.000Z"},
                            "seats": 293,
                            "code": "Y",
                            "priority": 4,
                            "name": "Economy",
                            "booking_classes": "SYBHKLMNQTVXGUE",
                            "three_comp_code": "Y",
                        },
                        {
                            "curtain_version": "",
                            "compartment": "Y",
                            "valid_since": {"$date": "2025-01-01T00:00:00.000Z"},
                            "valid_until": {"$date": "2025-12-31T00:00:00.000Z"},
                            "seats": 293,
                            "code": "Y",
                            "priority": 4,
                            "name": "Economy",
                            "booking_classes": "SYBHKLMNQTVXGUE",
                            "three_comp_code": "Y",
                        },
                        {
                            "curtain_version": "",
                            "compartment": "F",
                            "valid_since": {"$date": "2025-01-01T00:00:00.000Z"},
                            "valid_until": {"$date": "2025-12-31T00:00:00.000Z"},
                            "seats": 0,
                            "code": "F",
                            "priority": 1,
                            "name": "First",
                            "booking_classes": "PFA",
                            "three_comp_code": "F",
                        },
                        {
                            "curtain_version": "",
                            "compartment": "J",
                            "valid_since": {"$date": "2025-01-01T00:00:00.000Z"},
                            "valid_until": {"$date": "2025-12-31T00:00:00.000Z"},
                            "seats": 24,
                            "code": "J",
                            "priority": 2,
                            "name": "Business",
                            "booking_classes": "JCDIZ",
                            "three_comp_code": "C",
                        },
                        {
                            "curtain_version": "",
                            "compartment": "W",
                            "valid_since": {"$date": "2025-01-01T00:00:00.000Z"},
                            "valid_until": {"$date": "2025-12-31T00:00:00.000Z"},
                            "seats": 0,
                            "code": "W",
                            "priority": 3,
                            "name": "Premium Eco",
                            "booking_classes": "W",
                            "three_comp_code": "Y",
                        },
                        {
                            "curtain_version": "",
                            "compartment": "F",
                            "valid_since": {"$date": "2026-01-01T00:00:00.000Z"},
                            "valid_until": {"$date": "2035-12-31T00:00:00.000Z"},
                            "seats": 0,
                            "code": "F",
                            "priority": 1,
                            "name": "First",
                            "booking_classes": "PFA",
                            "three_comp_code": "F",
                        },
                        {
                            "curtain_version": "",
                            "compartment": "J",
                            "valid_since": {"$date": "2026-01-01T00:00:00.000Z"},
                            "valid_until": {"$date": "2035-12-31T00:00:00.000Z"},
                            "seats": 24,
                            "code": "J",
                            "priority": 2,
                            "name": "Business",
                            "booking_classes": "JCDIZ",
                            "three_comp_code": "C",
                        },
                        {
                            "curtain_version": "",
                            "compartment": "W",
                            "valid_since": {"$date": "2026-01-01T00:00:00.000Z"},
                            "valid_until": {"$date": "2035-12-31T00:00:00.000Z"},
                            "seats": 0,
                            "code": "W",
                            "priority": 3,
                            "name": "Premium Eco",
                            "booking_classes": "W",
                            "three_comp_code": "Y",
                        },
                        {
                            "curtain_version": "",
                            "compartment": "Y",
                            "valid_since": {"$date": "2026-01-01T00:00:00.000Z"},
                            "valid_until": {"$date": "2035-12-31T00:00:00.000Z"},
                            "seats": 293,
                            "code": "Y",
                            "priority": 4,
                            "name": "Economy",
                            "booking_classes": "SYBHKLMNQTVXGUE",
                            "three_comp_code": "Y",
                        },
                    ],
                    "aircraft_restriction": [
                        {
                            "r_no": 431427,
                            "update_no": 1,
                            "restr_type": "M",
                            "mark": "Y",
                            "technical_reason": None,
                            "workorder_no": None,
                            "remark": None,
                            "valid_since": {"$date": "2025-11-12T00:00:00.000Z"},
                            "valid_until": {"$date": "2035-12-31T00:00:00.000Z"},
                            "expire_date": None,
                            "expire_total_fh_hours": None,
                            "expire_total_fh_minutes": None,
                            "expire_total_cycles": None,
                            "entry_dt": {"$date": "2025-11-12T06:38:02.000Z"},
                            "entry_user": "ENGCNG",
                            "ata_chapter": None,
                            "ata_subchapter": None,
                            "ata_section": None,
                            "ata_item": None,
                            "ata_description": "S794-T-72 ENGINE, (RR) - FAIRING/SPINNER - AIR INTAKE, ENGINE 1 NO.1 ENG AIR INTAKE FAIRING, A PART OF POLYURETHANE VARN",
                            "description": "ENGNO.1 AIR INTAKE FAIRING, A PART OF POLYURETHANE VARNISH FOUND MISSING.",
                            "limitations": "OTHER   AMM 72-35-41-20",
                            "operating_state": "N",
                            "telex": "N",
                            "message": None,
                            "sender_object_id": "20251112BLBKS794",
                            "ack_state": "A",
                            "ack_date": {"$date": "2025-11-12T06:38:00.000Z"},
                            "ack_user": "ENGCNG",
                            "constraint_code": [],
                        },
                        {
                            "r_no": 431480,
                            "update_no": 1,
                            "restr_type": "M",
                            "mark": "Y",
                            "technical_reason": None,
                            "workorder_no": None,
                            "remark": None,
                            "valid_since": {"$date": "2025-11-12T00:00:00.000Z"},
                            "valid_until": {"$date": "2035-12-31T00:00:00.000Z"},
                            "expire_date": None,
                            "expire_total_fh_hours": None,
                            "expire_total_fh_minutes": None,
                            "expire_total_cycles": None,
                            "entry_dt": {"$date": "2025-11-13T00:34:42.000Z"},
                            "entry_user": "ENGDAN",
                            "ata_chapter": None,
                            "ata_subchapter": None,
                            "ata_section": None,
                            "ata_item": None,
                            "ata_description": "S795-T-MAINT STATUS - BMC 2 L WING LOOP A INOP  Phase of Flight: Taxi-out",
                            "description": "MAINT STATUS - BMC 2L WING LOOP A INOP Phase of Flight: Taxi-out",
                            "limitations": "OTHER   MEL HOW P 7/32",
                            "operating_state": "N",
                            "telex": "N",
                            "message": None,
                            "sender_object_id": "20251112BLBKS795",
                            "ack_state": "A",
                            "ack_date": {"$date": "2025-11-13T00:34:43.000Z"},
                            "ack_user": "ENGDAN",
                            "constraint_code": [],
                        },
                        {
                            "r_no": 410408,
                            "update_no": 6,
                            "restr_type": "M",
                            "mark": "Y",
                            "technical_reason": None,
                            "workorder_no": None,
                            "remark": None,
                            "valid_since": {"$date": "2025-02-20T00:00:00.000Z"},
                            "valid_until": {"$date": "2035-12-31T00:00:00.000Z"},
                            "expire_date": None,
                            "expire_total_fh_hours": None,
                            "expire_total_fh_minutes": None,
                            "expire_total_cycles": None,
                            "entry_dt": {"$date": "2025-07-22T17:29:20.000Z"},
                            "entry_user": "ENGEC",
                            "ata_chapter": None,
                            "ata_subchapter": None,
                            "ata_section": None,
                            "ata_item": None,
                            "ata_description": "S710- ENGINE 2 REF SWC-29677, PLS REPLACE ENG#2 LH T/R  12 O'CLOCK REAR DUCT FAIRING IAW SAFRA",
                            "description": "SPECIAL WORK CARD (SWC), ENGINE 2 REF SWC-29677, PLS REPLACE ENG#2 LH T/R  12 O'CLOCK REAR DUCT FAIRING IAW SAFRAN CMM 78-30-20 FRSX092 ON OR BEFORE 800FC OR NEXT C-CHECK  WHICHEVER OCCURS FIRST.",
                            "limitations": "OTHER   SWC-29677",
                            "operating_state": "N",
                            "telex": "Y",
                            "message": None,
                            "sender_object_id": "20250220BLBKS710",
                            "ack_state": "A",
                            "ack_date": {"$date": "2025-04-08T16:04:59.000Z"},
                            "ack_user": "ENGAMB",
                            "constraint_code": [],
                        },
                        {
                            "r_no": 410410,
                            "update_no": 6,
                            "restr_type": "M",
                            "mark": "Y",
                            "technical_reason": None,
                            "workorder_no": None,
                            "remark": None,
                            "valid_since": {"$date": "2025-02-20T00:00:00.000Z"},
                            "valid_until": {"$date": "2035-12-31T00:00:00.000Z"},
                            "expire_date": None,
                            "expire_total_fh_hours": None,
                            "expire_total_fh_minutes": None,
                            "expire_total_cycles": None,
                            "entry_dt": {"$date": "2025-07-22T17:29:04.000Z"},
                            "entry_user": "ENGEC",
                            "ata_chapter": None,
                            "ata_subchapter": None,
                            "ata_section": None,
                            "ata_item": None,
                            "ata_description": "S711- REF SWC-29677, PLS REPLACE ENG#2 RH T/R  12 O'CLOCK REAR DUCT FAIRING",
                            "description": "SPECIAL WORK CARD (SWC), ENGINE 2 REF SWC-29677, PLS REPLACE ENG#2 RH T/R  12 O'CLOCK REAR DUCT FAIRING IAW SAFRAN CMM 78-30-20 FRSX092 ON OR BEFORE 800FC OR NEXT C-CHECK  WHICHEVER OCCURS FIRST.",
                            "limitations": "OTHER   SWC-29677",
                            "operating_state": "N",
                            "telex": "Y",
                            "message": None,
                            "sender_object_id": "20250220BLBKS711",
                            "ack_state": "A",
                            "ack_date": {"$date": "2025-04-08T15:36:04.000Z"},
                            "ack_user": "ENGAMB",
                            "constraint_code": [],
                        },
                        {
                            "r_no": 431871,
                            "update_no": 1,
                            "restr_type": "M",
                            "mark": "Y",
                            "technical_reason": None,
                            "workorder_no": None,
                            "remark": None,
                            "valid_since": {"$date": "2025-11-17T00:00:00.000Z"},
                            "valid_until": {"$date": "2035-12-31T00:00:00.000Z"},
                            "expire_date": None,
                            "expire_total_fh_hours": None,
                            "expire_total_fh_minutes": None,
                            "expire_total_cycles": None,
                            "entry_dt": {"$date": "2025-11-17T09:56:42.000Z"},
                            "entry_user": "ENGFFN",
                            "ata_chapter": "49",
                            "ata_subchapter": "10",
                            "ata_section": "01A",
                            "ata_item": None,
                            "ata_description": "S798-C-49 AIRBORNE AUXILIARY POWER APU AUTO SHUTDOWN.",
                            "description": "49 AIRBORNE AUXILIARY POWERAPU AUTO SHUTDOWN.",
                            "limitations": "MEL     49-10-01A",
                            "operating_state": "N",
                            "telex": "N",
                            "message": None,
                            "sender_object_id": "20251117BLBKS798",
                            "ack_state": "A",
                            "ack_date": {"$date": "2025-11-17T09:56:41.000Z"},
                            "ack_user": "ENGFFN",
                            "constraint_code": ["APU", "APU (RED ALERT)"],
                        },
                        {
                            "r_no": 421626,
                            "update_no": 1,
                            "restr_type": "M",
                            "mark": "Y",
                            "technical_reason": None,
                            "workorder_no": None,
                            "remark": None,
                            "valid_since": {"$date": "2025-07-22T00:00:00.000Z"},
                            "valid_until": {"$date": "2035-12-31T00:00:00.000Z"},
                            "expire_date": None,
                            "expire_total_fh_hours": None,
                            "expire_total_fh_minutes": None,
                            "expire_total_cycles": None,
                            "entry_dt": {"$date": "2025-07-22T17:26:21.000Z"},
                            "entry_user": "ENGEC",
                            "ata_chapter": None,
                            "ata_subchapter": None,
                            "ata_section": None,
                            "ata_item": None,
                            "ata_description": "S754- ENG#2 LH THRUST REVERSER UPPER COVE FAIRING FOUND SOME SE",
                            "description": "SPECIAL WORK CARD (SWC), ENGINE 2REF SWC-29677 REV.00, ENG#2 LH THRUST REVERSER UPPER COVE FAIRING FOUND SOME SEALANT DETACHED. SUBJECT SEALANT REMOVED AND INSPECTION PERFORMED WITH NO LOOSE/ MISSING FASTENER. SEALANT RE-APPLIED. PLS PERFORM REPEAT GVI",
                            "limitations": "OTHER   SWC-29677 REV 0",
                            "operating_state": "N",
                            "telex": "Y",
                            "message": None,
                            "sender_object_id": "20250722BLBKS754",
                            "ack_state": "A",
                            "ack_date": {"$date": "2025-07-22T17:26:21.000Z"},
                            "ack_user": "ENGEC",
                            "constraint_code": [],
                        },
                        {
                            "r_no": 421627,
                            "update_no": 1,
                            "restr_type": "M",
                            "mark": "Y",
                            "technical_reason": None,
                            "workorder_no": None,
                            "remark": None,
                            "valid_since": {"$date": "2025-07-22T00:00:00.000Z"},
                            "valid_until": {"$date": "2035-12-31T00:00:00.000Z"},
                            "expire_date": None,
                            "expire_total_fh_hours": None,
                            "expire_total_fh_minutes": None,
                            "expire_total_cycles": None,
                            "entry_dt": {"$date": "2025-07-22T17:26:52.000Z"},
                            "entry_user": "ENGEC",
                            "ata_chapter": None,
                            "ata_subchapter": None,
                            "ata_section": None,
                            "ata_item": None,
                            "ata_description": "S755- ENG#2 RH THRUST REVERSER UPPER COVE FAIRING FOUND SOME SE",
                            "description": "SPECIAL WORK CARD (SWC), ENGINE 2REF SWC-29677 REV.00, ENG#2 RH THRUST REVERSER UPPER COVE FAIRING FOUND SOME SEALANT MISSING. SUBJECT SEALANT REMOVED AND INSPECTION PERFORMED WITH NO LOOSE/ MISSING FASTENER. SEALANT RE-APPLIED. PLS PERFORM REPEAT GVI I",
                            "limitations": "OTHER   SWC-29677 REV 0",
                            "operating_state": "N",
                            "telex": "Y",
                            "message": None,
                            "sender_object_id": "20250722BLBKS755",
                            "ack_state": "A",
                            "ack_date": {"$date": "2025-07-22T17:26:52.000Z"},
                            "ack_user": "ENGEC",
                            "constraint_code": [],
                        },
                        {
                            "r_no": 429284,
                            "update_no": 1,
                            "restr_type": "M",
                            "mark": "Y",
                            "technical_reason": None,
                            "workorder_no": None,
                            "remark": None,
                            "valid_since": {"$date": "2025-10-17T00:00:00.000Z"},
                            "valid_until": {"$date": "2035-12-31T00:00:00.000Z"},
                            "expire_date": None,
                            "expire_total_fh_hours": None,
                            "expire_total_fh_minutes": None,
                            "expire_total_cycles": None,
                            "entry_dt": {"$date": "2025-10-17T16:55:03.000Z"},
                            "entry_user": "ENGDAN",
                            "ata_chapter": None,
                            "ata_subchapter": None,
                            "ata_section": None,
                            "ata_item": None,
                            "ata_description": "S782-T-55 STABILIZERS, ELEVATOR SPAR BOX WAC FOUND R/H ELEVATOR TRAILING EDGE LOWER FILLER MISSING PHOTO ATTACHED",
                            "description": "55 STABILIZERS, ELEVATOR SPAR BOXWAC FOUND R/H ELEVATOR TRAILING EDGE LOWER FILLER MISSINGPHOTO ATTACHED",
                            "limitations": "OTHER   SRM 55-21-11-28",
                            "operating_state": "N",
                            "telex": "N",
                            "message": None,
                            "sender_object_id": "20251017BLBKS782",
                            "ack_state": "A",
                            "ack_date": {"$date": "2025-10-17T16:55:03.000Z"},
                            "ack_user": "ENGDAN",
                            "constraint_code": [],
                        },
                    ],
                    "aircraft_owner": "CX",
                    "aircraft_subtype": "333",
                    "fleet_print_code": "333",
                    "rotational_flag": "Y",
                    "standard_configuration": "STN",
                    "payload": None,
                    "mtom": None,
                    "max_range": None,
                    "noise_category": None,
                    "average_speed": None,
                    "aircraft_group": "330",
                    "icao_code": "333",
                    "name": "Airbus Industrie A330-300",
                    "body_type": "W",
                    "category": "J",
                }
            ]
        }


if __name__ == "__main__":
    """
    Test script to validate the AircraftConfiguration schema against the
    JSON dataset.
    """
    import sys
    from pydantic import ValidationError
    from pandas import Timestamp
    from bson import ObjectId

    data = {
        "registration": "BLXN",
        "valid_since": Timestamp("2021-06-21 00:00:00"),
        "valid_until": Timestamp("2035-12-31 00:00:00"),
        "ac_operator": "CX",
        "ac_owner": "CX",
        "ac_subtype": "35J",
        "homebase": None,
        "ac_logical_no": 15,
        "ac_state": "R",
        "dry_operating_wgt": 0,
        "max_takeoff_wgt": 268000,
        "cargo_capacity": 0,
        "fuel_capacity": 0,
        "avg_fuel_consump": 0,
        "ac_index": 15,
        "crewsize_cockpit": 0,
        "crewsize_cabin": 0,
        "std_version": "STN",
        "ap_restriction": "N",
        "ac_owner_name": "CX",
        "ac_subtype_name": "35J",
        "ac_category": "J",
        "remark": "46J/32W/256Y = 334",
        "fuel_measure_unit": "kg",
        "ac_callsign": None,
        "radio": None,
        "noise": None,
        "phone": None,
        "special_equipment": None,
        "acars": "S",
        "alt_reg": None,
        "record_id": 608495,
        "last_update": Timestamp("2022-03-02 10:36:43"),
        "last_update_user_id": "netline",
        "std_version_alt_1": None,
        "std_version_alt_2": None,
        "std_version_alt_3": None,
        "std_version_alt_4": None,
        "ils_equipment": "I",
        "autoland": "Y",
        "metadata": {
            "dagster_run_id": "89f45534-0aa2-431b-b464-3bd6009cc8d8",
            "dagster_job_name": "nlo_replica_1hr_dimension_table_job",
            "dagster_asset_name": "aircraft_configuration_serve",
            "processed_timestamp": datetime(2025, 11, 18, 2, 31, 2, 938512),
        },
        "_id": ObjectId("691aed6a0c9a5eb523000d1f"),
    }

    try:
        # Validate the data against the AircraftConfiguration schema
        validated_data = AircraftConfigurationApi(**data)
        print("✓ Validation successful!")
        print(f"Validated record: {validated_data.registration}")
    except ValidationError as e:
        print("✗ Validation failed!")
        print(f"Errors: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)

# if __name__ == "__main__":
#     """
#     Test script to validate the AircraftConfiguration schema against the
#     JSON dataset.
#     """
#     import json
#     import sys
#     from pathlib import Path
#     from pydantic import ValidationError

#     # Configure logging for standalone execution
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(levelname)s - %(message)s'
#     )

#     # Locate the JSON file
#     json_file = Path(__file__).resolve()
#     logger.info(f"Script location: {json_file}")
#     json_path = json_file.with_suffix('.json')
#     logger.info(f"Looking for JSON file at: {json_path}")

#     if not json_path.exists():
#         logger.error(f"JSON file not found: {json_path}")
#         sys.exit(1)

#     # Load the JSON data
#     logger.info("Loading JSON data...")
#     with open(json_path, 'r') as f:
#         data = json.load(f)

#     logger.info(f"Loaded {len(data)} records from JSON file")

#     # Statistics
#     total_records = len(data)
#     successful_validations = 0
#     failed_validations = 0
#     validation_errors = []

#     # Test each record
#     logger.info("Starting validation...")
#     for idx, record in enumerate(data, 1):
#         try:
#             # Remove MongoDB-specific fields
#             if '_id' in record:
#                 del record['_id']

#             # Convert MongoDB date format to ISO string
#             def convert_dates(obj):
#                 if isinstance(obj, dict):
#                     if '$date' in obj:
#                         return obj['$date']
#                     return {k: convert_dates(v) for k, v in obj.items()}
#                 elif isinstance(obj, list):
#                     return [convert_dates(item) for item in obj]
#                 return obj

#             record = convert_dates(record)

#             # Validate the record
#             aircraft_config = AircraftConfiguration(**record)
#             successful_validations += 1

#             # Log first successful validation as example
#             if successful_validations == 1:
#                 logger.info("✓ First record validated successfully:")
#                 logger.info(
#                     f"  Registration: {aircraft_config.registration}"
#                 )
#                 logger.info(
#                     f"  AC Subtype: {aircraft_config.ac_subtype}"
#                 )
#                 logger.info(
#                     f"  Valid Since: {aircraft_config.valid_since}"
#                 )
#                 logger.info(
#                     f"  Compartments: "
#                     f"{len(aircraft_config.aircraft_compartment)}"
#                 )
#                 logger.info(
#                     f"  Restrictions: "
#                     f"{len(aircraft_config.aircraft_restriction)}"
#                 )

#         except ValidationError as e:
#             failed_validations += 1
#             error_info = {
#                 'record_index': idx,
#                 'registration': record.get('registration', 'UNKNOWN'),
#                 'errors': e.errors()
#             }
#             validation_errors.append(error_info)

#             # Log first few errors in detail
#             if failed_validations <= 3:
#                 reg = record.get('registration', 'UNKNOWN')
#                 logger.error(
#                     f"✗ Validation failed for record {idx} "
#                     f"(Registration: {reg})"
#                 )
#                 logger.error(f"  Errors: {e.errors()}")

#         except Exception as e:
#             failed_validations += 1
#             error_info = {
#                 'record_index': idx,
#                 'registration': record.get('registration', 'UNKNOWN'),
#                 'errors': str(e)
#             }
#             validation_errors.append(error_info)
#             logger.error(f"✗ Unexpected error for record {idx}: {e}")

#         # Progress indicator every 100 records
#         if idx % 100 == 0:
#             logger.info(
#                 f"Progress: {idx}/{total_records} records processed..."
#             )

#     # Summary
#     logger.info("\n" + "="*70)
#     logger.info("VALIDATION SUMMARY")
#     logger.info("="*70)
#     logger.info(f"Total Records:        {total_records}")
#     success_pct = successful_validations/total_records*100
#     logger.info(
#         f"Successful:           {successful_validations} "
#         f"({success_pct:.2f}%)"
#     )
#     fail_pct = failed_validations/total_records*100
#     logger.info(
#         f"Failed:               {failed_validations} ({fail_pct:.2f}%)"
#     )
#     logger.info("="*70)

#     # Show error breakdown if there are failures
#     if failed_validations > 0:
#         logger.warning(
#             f"\n{failed_validations} validation errors found."
#         )
#         logger.warning("First 5 failed records:")
#         for error_info in validation_errors[:5]:
#             reg = error_info['registration']
#             idx_val = error_info['record_index']
#             logger.warning(
#                 f"  - Record {idx_val} (Registration: {reg})"
#             )
#             if isinstance(error_info['errors'], list):
#                 # Show first 2 errors per record
#                 for err in error_info['errors'][:2]:
#                     logger.warning(f"    • {err}")
#             else:
#                 logger.warning(f"    • {error_info['errors']}")

#         # Save detailed errors to file
#         error_file = json_file.with_name('validation_errors.json')
#         with open(error_file, 'w') as f:
#             json.dump(validation_errors, f, indent=2, default=str)
#         logger.info(f"\nDetailed errors saved to: {error_file}")
#     else:
#         logger.info("\n✓ All records validated successfully!")
#         logger.info("Schema is correctly built and matches the dataset.")

#     # Exit with appropriate code
#     sys.exit(0 if failed_validations == 0 else 1)
