import enum


class Billing(enum.StrEnum):
    CLIENT_BILL = "client_bill"
    COMMERCIAL_INSURANCE = "commercial_insurance"
    PATIENT_BILL_PASSTHROUGH = "patient_bill_passthrough"
    PATIENT_BILL = "patient_bill"

    def to_hl7(self) -> str:
        return {
            Billing.CLIENT_BILL: "C",
            Billing.COMMERCIAL_INSURANCE: "T",
            Billing.PATIENT_BILL_PASSTHROUGH: "C",
            Billing.PATIENT_BILL: "P",
        }[self]
