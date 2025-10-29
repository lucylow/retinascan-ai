from datetime import datetime
from fpdf import FPDF


class MultilingualReportGenerator:
    """
    Generate localized patient reports.
    """

    def __init__(self, language: str = "en") -> None:
        self.language = language
        self.translations = self._load_translations()

    def _load_translations(self) -> dict:
        return {
            "en": {
                "title": "Retinal Screening Report",
                "disclaimer": (
                    "This is an AI-assisted screening tool. Final diagnosis should be made by a qualified ophthalmologist."
                ),
                "referral_urgent": "URGENT: Please see an ophthalmologist within 1 week",
                "referral_routine": "Schedule follow-up with eye specialist within 3 months",
                "no_referral": "Continue regular annual screening",
            },
            "fr": {
                "title": "Rapport de Dépistage Rétinien",
                "disclaimer": (
                    "Ceci est un outil de dépistage assisté par IA. Le diagnostic final doit être posé par un ophtalmologiste qualifié."
                ),
                "referral_urgent": "URGENT: Consultez un ophtalmologiste dans la semaine",
                "referral_routine": "Prenez rendez-vous avec un spécialiste dans les 3 mois",
                "no_referral": "Continuez le dépistage annuel régulier",
            },
            "wo": {
                "title": "Rapoor bu Xët bu Bët",
                "disclaimer": (
                    "Loolu mooy jumtukaay xët bu am AI. Diagnostic bu muj war na def doktor bët bu am diplom."
                ),
                "referral_urgent": "URGENT: Gëna nga xool doktor bët ci ayu-bis",
                "referral_routine": "Bind randevou ak specialist ci 3 weer",
                "no_referral": "Koy woyofal ci ayu-benn ci at",
            },
            "sw": {
                "title": "Ripoti ya Uchunguzi wa Retina",
                "disclaimer": (
                    "Hii ni zana ya uchunguzi inayosaidiana na AI. Utambuzi wa mwisho unapaswa kufanywa na daktari wa macho mwenye sifa."
                ),
                "referral_urgent": "DHARURA: Tafadhali ona daktari wa macho ndani ya wiki 1",
                "referral_routine": "Panga kukutana na mtaalamu wa macho ndani ya miezi 3",
                "no_referral": "Endelea na uchunguzi wa kila mwaka",
            },
            "ar": {
                "title": "تقرير فحص الشبكية",
                "disclaimer": (
                    "هذه أداة فحص بمساعدة الذكاء الاصطناعي. يجب أن يتم التشخيص النهائي من قبل طبيب عيون مؤهل."
                ),
                "referral_urgent": "عاجل: يرجى مراجعة طبيب العيون خلال أسبوع واحد",
                "referral_routine": "حدد موعداً مع أخصائي العيون خلال 3 أشهر",
                "no_referral": "استمر في الفحص السنوي المنتظم",
            },
        }

    def generate_report(self, patient_data: dict, screening_results: dict) -> dict:
        lang = self.translations.get(self.language, self.translations["en"])
        report = {
            "report_id": f"RS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "language": self.language,
            "title": lang["title"],
            "patient": {
                "name": patient_data.get("name", "N/A"),
                "age": patient_data.get("age", "N/A"),
                "id": patient_data.get("patient_id", "N/A"),
            },
            "screening_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "results": {
                "dr_grade": screening_results.get("dr_grade", "N/A"),
                "confidence": f"{screening_results.get('dr_confidence', 0.0)*100:.1f}%",
                "glaucoma_risk": screening_results.get("glaucoma_risk", "N/A"),
                "amd_risk": screening_results.get("amd_risk", "N/A"),
                "cvd_risk": screening_results.get("cvd_risk", "N/A"),
                "kidney_risk": screening_results.get("kidney_risk", "N/A"),
            },
            "recommendation": self._get_recommendation(screening_results, lang),
            "quality_note": screening_results.get("image_quality", "Good"),
            "disclaimer": lang["disclaimer"],
        }
        return report

    def _get_recommendation(self, results: dict, lang: dict) -> str:
        if results.get("requires_referral"):
            if results.get("dr_grade") in ["Severe", "Proliferative DR"]:
                return lang["referral_urgent"]
            return lang["referral_routine"]
        return lang["no_referral"]

    def export_pdf(self, report: dict, filename: str = "retinascan_report.pdf") -> str:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, report["title"], ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Patient: {report['patient']['name']}", ln=True)
        pdf.cell(0, 10, f"Date: {report['screening_date']}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Results:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"DR Status: {report['results']['dr_grade']}", ln=True)
        pdf.cell(0, 10, f"Confidence: {report['results']['confidence']}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Recommendation:", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, report["recommendation"])
        pdf.ln(5)

        pdf.set_font("Arial", "I", 10)
        pdf.multi_cell(0, 10, report["disclaimer"])

        pdf.output(filename)
        return filename


report_gen = MultilingualReportGenerator(language="en")


