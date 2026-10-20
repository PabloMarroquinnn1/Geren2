import argparse
import html
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "datos" / "materiales_operativos_60.json"
DEFAULT_OUTPUT = ROOT / "assets" / "brand" / "internal_materials"
PALETTE = ["#087F5B", "#F28C28", "#197C91", "#6C5B7B", "#3A7D44", "#D97706"]


def icon_markup(kind, primary, secondary):
    """Small original vector illustrations; each item gets its own labeled image."""
    p, s = primary, secondary
    icons = {
        "chair": f'<path d="M115 45h125v120H115z" fill="{p}"/><path d="M100 165h160v45H100z" fill="{s}"/><path d="M125 210l-20 65M235 210l20 65" stroke="#24343B" stroke-width="16" stroke-linecap="round"/><path d="M160 210v35M200 210v35" stroke="#24343B" stroke-width="12" stroke-linecap="round"/>',
        "desk": f'<path d="M55 90h250v42H55z" fill="{p}"/><path d="M75 132v135M285 132v135" stroke="#24343B" stroke-width="18"/><path d="M105 142h65v77h-65z" fill="{s}"/><path d="M188 155h70" stroke="#FFFFFF" stroke-width="8"/>',
        "worktable": f'<path d="M45 115h270v45H45z" fill="{p}"/><path d="M70 160v112M290 160v112" stroke="#24343B" stroke-width="18"/><path d="M95 174h170" stroke="{s}" stroke-width="12"/>',
        "table": f'<path d="M70 105h220v40H70z" fill="{p}"/><path d="M95 145v125M265 145v125" stroke="#24343B" stroke-width="16"/><path d="M110 270h140" stroke="{s}" stroke-width="14" stroke-linecap="round"/>',
        "shelf": f'<path d="M75 35v245M285 35v245" stroke="#24343B" stroke-width="16"/><path d="M65 75h230M65 155h230M65 235h230" stroke="{p}" stroke-width="20"/><path d="M85 43h190" stroke="{s}" stroke-width="10"/>',
        "cabinet": f'<rect x="85" y="35" width="200" height="245" rx="12" fill="{p}"/><path d="M95 92h180M95 150h180M95 208h180" stroke="#FFFFFF" stroke-width="7"/><circle cx="250" cy="65" r="6" fill="{s}"/><circle cx="250" cy="122" r="6" fill="{s}"/><circle cx="250" cy="181" r="6" fill="{s}"/><circle cx="250" cy="239" r="6" fill="{s}"/>',
        "locker": f'<rect x="90" y="28" width="190" height="252" rx="12" fill="{p}"/><path d="M185 35v238" stroke="#FFFFFF" stroke-width="7"/><path d="M120 65h38M215 65h38" stroke="{s}" stroke-width="9"/><circle cx="165" cy="155" r="6" fill="#FFFFFF"/><circle cx="205" cy="155" r="6" fill="#FFFFFF"/>',
        "counter": f'<path d="M55 95h250v52H55z" fill="{s}"/><path d="M75 147h210v125H75z" fill="{p}"/><path d="M100 172h160v18H100z" fill="#FFFFFF" opacity=".85"/><path d="M110 220h55v52h-55z" fill="#FFFFFF" opacity=".22"/>',
        "workbench": f'<path d="M50 95h260v42H50z" fill="{p}"/><path d="M72 137v135M288 137v135" stroke="#24343B" stroke-width="18"/><path d="M110 65h140v28H110z" fill="{s}"/><path d="M115 180h130" stroke="#FFFFFF" stroke-width="9"/>',
        "bin": f'<path d="M95 70h180l-18 200H113z" fill="{p}"/><path d="M80 55h210v24H80z" fill="{s}"/><path d="M120 105v130M175 105v130M230 105v130" stroke="#FFFFFF" stroke-width="9" opacity=".8"/><circle cx="135" cy="284" r="15" fill="#24343B"/><circle cx="235" cy="284" r="15" fill="#24343B"/>',
        "box": f'<path d="M55 95l125-58 125 58v147l-125 58-125-58z" fill="{p}"/><path d="M55 95l125 58 125-58M180 153v147" fill="none" stroke="#FFFFFF" stroke-width="12"/><path d="M145 56h70v65h-70z" fill="{s}" opacity=".92"/>',
        "crate": f'<path d="M58 83h244v185H58z" rx="14" fill="{p}"/><path d="M58 115h244M80 117v131M130 117v131M180 117v131M230 117v131M280 117v131" stroke="#FFFFFF" stroke-width="10" opacity=".9"/><path d="M88 75h185" stroke="{s}" stroke-width="16"/>',
        "pallet": f'<path d="M60 95h240v115H60z" fill="{p}"/><path d="M60 125h240M60 170h240M90 210v55M180 210v55M270 210v55" stroke="#FFFFFF" stroke-width="13"/><path d="M48 265h264" stroke="{s}" stroke-width="18" stroke-linecap="round"/>',
        "roll": f'<ellipse cx="180" cy="78" rx="75" ry="35" fill="{s}"/><path d="M105 78v145c0 24 150 24 150 0V78" fill="{p}"/><ellipse cx="180" cy="223" rx="75" ry="35" fill="{p}"/><ellipse cx="180" cy="79" rx="28" ry="13" fill="#F4F7F5"/><path d="M118 115h124" stroke="#FFFFFF" stroke-width="8" opacity=".8"/>',
        "bubble": f'<rect x="70" y="45" width="220" height="225" rx="18" fill="{p}"/><path d="M70 90h220M70 145h220M70 200h220M125 45v225M180 45v225M235 45v225" stroke="#FFFFFF" stroke-width="7" opacity=".82"/>' + ''.join(f'<circle cx="{x}" cy="{y}" r="13" fill="{s}" opacity=".9"/>' for x,y in [(98,67),(155,117),(210,172),(265,226)]),
        "tape": f'<circle cx="180" cy="155" r="112" fill="{p}"/><circle cx="180" cy="155" r="57" fill="#F4F7F5"/><circle cx="180" cy="155" r="32" fill="{s}"/><path d="M270 75l38-32" stroke="#24343B" stroke-width="14" stroke-linecap="round"/>',
        "tape-dispenser": f'<path d="M55 175h220l45 62H85z" fill="{p}"/><circle cx="135" cy="153" r="66" fill="{s}"/><circle cx="135" cy="153" r="33" fill="#F4F7F5"/><path d="M265 165l66 72h-53l-25-34z" fill="#24343B"/>',
        "label-roll": f'<rect x="75" y="75" width="175" height="175" rx="16" fill="{p}"/><circle cx="250" cy="162" r="84" fill="{s}"/><circle cx="250" cy="162" r="34" fill="#F4F7F5"/><path d="M95 115h110M95 150h90M95 185h105" stroke="#FFFFFF" stroke-width="9"/>',
        "strap": f'<path d="M92 55h172v195H92z" fill="none" stroke="{p}" stroke-width="23"/><path d="M130 93h96v120h-96z" fill="none" stroke="{s}" stroke-width="17"/><path d="M178 45v32M178 240v30" stroke="#24343B" stroke-width="12"/>',
        "corner-protector": f'<path d="M85 45h74v165h145v74H85z" fill="{p}"/><path d="M115 73h28v112h133v29H115z" fill="{s}"/>',
        "envelope": f'<rect x="55" y="72" width="250" height="175" rx="18" fill="{p}"/><path d="M60 86l120 93 120-93M65 238l90-79M295 238l-90-79" fill="none" stroke="#FFFFFF" stroke-width="12"/><path d="M102 55h155v18H102z" fill="{s}"/>',
        "security-bag": f'<path d="M100 70h160l-12 205H112z" fill="{p}"/><path d="M100 73h160v38H100z" fill="{s}"/><path d="M125 145h110v62H125z" fill="#FFFFFF" opacity=".9"/><path d="M145 163h70M145 184h50" stroke="{p}" stroke-width="8"/>',
        "platform-cart": f'<path d="M58 95h225v32H58z" fill="{p}"/><path d="M80 127v90M263 127v90" stroke="#24343B" stroke-width="14"/><circle cx="92" cy="245" r="25" fill="#24343B"/><circle cx="250" cy="245" r="25" fill="#24343B"/><path d="M280 95h36l-28 62" stroke="{s}" stroke-width="15" stroke-linecap="round"/><path d="M95 78h150" stroke="{s}" stroke-width="13"/>',
        "hand-truck": f'<path d="M118 38v210h100" fill="none" stroke="{p}" stroke-width="22" stroke-linecap="round"/><path d="M103 242h158" stroke="{s}" stroke-width="20" stroke-linecap="round"/><circle cx="120" cy="270" r="25" fill="#24343B"/><circle cx="240" cy="270" r="25" fill="#24343B"/><path d="M140 88h100" stroke="#24343B" stroke-width="14"/>',
        "pallet-jack": f'<path d="M95 95h120v104H95z" fill="{p}"/><path d="M215 120h88v24M215 174h88v-24" fill="none" stroke="{s}" stroke-width="15"/><path d="M130 199v50M235 199v50" stroke="#24343B" stroke-width="14"/><circle cx="128" cy="264" r="23" fill="#24343B"/><circle cx="240" cy="264" r="23" fill="#24343B"/><path d="M90 74h60v21" fill="none" stroke="#24343B" stroke-width="13"/>',
        "floor-scale": f'<rect x="70" y="145" width="220" height="100" rx="18" fill="{p}"/><rect x="115" y="70" width="130" height="58" rx="12" fill="{s}"/><rect x="133" y="87" width="94" height="24" rx="8" fill="#F4F7F5"/><path d="M115 247v28M245 247v28" stroke="#24343B" stroke-width="17"/>',
        "barcode-scanner": f'<path d="M85 55h135q48 0 48 47v52q0 32-30 32h-44l-28 102h-76l32-113q-37-10-37-53z" fill="{p}"/><path d="M112 82h113" stroke="{s}" stroke-width="14"/><path d="M239 70l75-25M250 95l83-3M249 123l80 20" stroke="#24343B" stroke-width="8"/>',
        "safety-cutter": f'<path d="M70 165l140-112 105 90-140 112z" fill="{p}"/><path d="M210 53l105 90 46-45-78-67z" fill="{s}"/><path d="M115 177l87-70" stroke="#FFFFFF" stroke-width="12"/>',
        "label-printer": f'<rect x="60" y="95" width="250" height="160" rx="22" fill="{p}"/><rect x="105" y="62" width="160" height="40" rx="10" fill="{s}"/><path d="M103 155h166v26H103z" fill="#F4F7F5"/><path d="M120 184v60M250 184v60" stroke="#24343B" stroke-width="10"/><circle cx="277" cy="127" r="9" fill="#FFFFFF"/>',
        "pos-terminal": f'<rect x="95" y="40" width="170" height="170" rx="22" fill="{p}"/><rect x="115" y="62" width="130" height="84" rx="12" fill="#F4F7F5"/><path d="M130 85h96M130 108h60" stroke="{s}" stroke-width="10"/><path d="M180 210v42M125 252h110" stroke="#24343B" stroke-width="14"/><circle cx="132" cy="176" r="8" fill="{s}"/>',
        "cash-drawer": f'<rect x="55" y="115" width="250" height="120" rx="18" fill="{p}"/><path d="M80 116V80h200v36" fill="{s}"/><path d="M80 155h200v54H80z" fill="#FFFFFF" opacity=".9"/><path d="M118 155v54M155 155v54M192 155v54M229 155v54" stroke="{p}" stroke-width="7"/><circle cx="180" cy="224" r="7" fill="#24343B"/>',
        "receipt-printer": f'<rect x="68" y="110" width="225" height="145" rx="23" fill="{p}"/><path d="M115 110V58h130v52" fill="{s}"/><path d="M132 65h98M132 85h75" stroke="#FFFFFF" stroke-width="9"/><path d="M120 165h122" stroke="#FFFFFF" stroke-width="12"/><circle cx="265" cy="145" r="9" fill="#FFFFFF"/>',
        "security-camera": f'<path d="M85 100h160l70 43-70 43H85z" fill="{p}"/><circle cx="250" cy="143" r="31" fill="#24343B"/><circle cx="250" cy="143" r="15" fill="{s}"/><path d="M130 100V67h100" fill="none" stroke="#24343B" stroke-width="14"/><path d="M180 186l-45 62" stroke="{s}" stroke-width="18"/>',
        "router": f'<rect x="68" y="150" width="230" height="90" rx="20" fill="{p}"/><path d="M120 151V70M245 151V70" stroke="#24343B" stroke-width="12"/><path d="M100 110q20-25 42 0M220 110q22-25 45 0" fill="none" stroke="{s}" stroke-width="12" stroke-linecap="round"/><circle cx="115" cy="202" r="8" fill="#FFFFFF"/><circle cx="150" cy="202" r="8" fill="#FFFFFF"/><circle cx="185" cy="202" r="8" fill="#FFFFFF"/>',
        "voltage-regulator": f'<rect x="95" y="45" width="170" height="225" rx="22" fill="{p}"/><rect x="125" y="75" width="110" height="63" rx="10" fill="#F4F7F5"/><path d="M143 120l25-35 18 22 16-16" fill="none" stroke="{s}" stroke-width="9"/><circle cx="145" cy="180" r="9" fill="#FFFFFF"/><circle cx="180" cy="180" r="9" fill="#FFFFFF"/><circle cx="215" cy="180" r="9" fill="#FFFFFF"/><path d="M145 270v20M215 270v20" stroke="#24343B" stroke-width="12"/>',
        "ups": f'<rect x="95" y="35" width="170" height="235" rx="22" fill="{p}"/><rect x="125" y="65" width="110" height="85" rx="12" fill="#F4F7F5"/><path d="M180 77l-24 42h25l-7 25 33-45h-26z" fill="{s}"/><circle cx="145" cy="190" r="9" fill="#FFFFFF"/><circle cx="180" cy="190" r="9" fill="#FFFFFF"/>',
        "desktop": f'<rect x="65" y="40" width="230" height="165" rx="18" fill="{p}"/><rect x="85" y="60" width="190" height="123" rx="8" fill="#F4F7F5"/><path d="M180 205v45M125 250h110" stroke="#24343B" stroke-width="16"/><rect x="120" y="258" width="120" height="22" rx="8" fill="{s}"/>',
        "monitor": f'<rect x="55" y="45" width="250" height="165" rx="18" fill="{p}"/><rect x="76" y="66" width="208" height="123" rx="8" fill="#F4F7F5"/><path d="M180 210v48M125 258h110" stroke="#24343B" stroke-width="16"/><path d="M105 155l45-42 38 29 43-54" fill="none" stroke="{s}" stroke-width="11"/>',
        "office-printer": f'<rect x="62" y="100" width="250" height="145" rx="22" fill="{p}"/><rect x="105" y="42" width="165" height="74" rx="10" fill="{s}"/><path d="M115 55h145M115 76h120" stroke="#FFFFFF" stroke-width="8"/><path d="M104 168h166v85H104z" fill="#F4F7F5"/><path d="M128 190h120M128 212h90" stroke="{p}" stroke-width="8"/>',
        "paper-letter": f'<path d="M95 35h145l55 55v190H95z" fill="{p}"/><path d="M240 35v57h55" fill="{s}"/><path d="M125 125h140M125 160h140M125 195h120M125 230h100" stroke="#FFFFFF" stroke-width="10"/>',
        "paper-legal": f'<path d="M105 25h135l55 55v205H105z" fill="{p}"/><path d="M240 25v57h55" fill="{s}"/><path d="M133 115h135M133 150h135M133 185h125M133 220h125" stroke="#FFFFFF" stroke-width="9"/>',
        "stapler": f'<path d="M62 175q15-100 110-112h92q45 0 45 42v47H62z" fill="{p}"/><path d="M75 182h240v52H75z" fill="{s}"/><path d="M120 125h143" stroke="#FFFFFF" stroke-width="12"/><circle cx="270" cy="208" r="8" fill="#24343B"/>',
        "hole-punch": f'<rect x="65" y="90" width="240" height="150" rx="45" fill="{p}"/><path d="M100 145h170" stroke="{s}" stroke-width="24"/><circle cx="130" cy="205" r="13" fill="#FFFFFF"/><circle cx="238" cy="205" r="13" fill="#FFFFFF"/><path d="M150 90V65h70v25" fill="none" stroke="#24343B" stroke-width="12"/>',
        "staples": f'<rect x="75" y="70" width="210" height="195" rx="18" fill="{p}"/><path d="M110 115h140M110 145h140M110 175h140M110 205h140" stroke="#FFFFFF" stroke-width="12"/><path d="M120 54h120" stroke="{s}" stroke-width="16"/>',
        "folder": f'<path d="M50 90h115l30 30h125v145H50z" fill="{p}"/><path d="M50 130h270" stroke="{s}" stroke-width="18"/><path d="M88 165h185M88 195h150" stroke="#FFFFFF" stroke-width="9"/>',
        "markers": f'<g transform="rotate(-16 180 160)"><rect x="65" y="95" width="225" height="42" rx="16" fill="{p}"/><path d="M65 95h52v42H65z" fill="{s}"/><path d="M290 95l40 21-40 21z" fill="#24343B"/><rect x="85" y="155" width="225" height="42" rx="16" fill="{s}"/><path d="M310 155l40 21-40 21z" fill="#24343B"/></g>',
        "pens": f'<g transform="rotate(-18 180 160)"><path d="M80 65h38v205H80zM142 65h38v205h-38zM204 65h38v205h-38z" fill="{p}"/><path d="M80 65h38v35H80zM142 65h38v35h-38zM204 65h38v35h-38z" fill="{s}"/><path d="M80 270l19 35 19-35M142 270l19 35 19-35M204 270l19 35 19-35" fill="#24343B"/></g>',
        "calculator": f'<rect x="95" y="25" width="170" height="255" rx="24" fill="{p}"/><rect x="120" y="55" width="120" height="58" rx="8" fill="#F4F7F5"/><path d="M135 78h90" stroke="{s}" stroke-width="9"/><g fill="{s}"><circle cx="140" cy="150" r="12"/><circle cx="180" cy="150" r="12"/><circle cx="220" cy="150" r="12"/><circle cx="140" cy="195" r="12"/><circle cx="180" cy="195" r="12"/><circle cx="220" cy="195" r="12"/></g>',
        "broom": f'<path d="M115 40l22 10-70 180-22-10z" fill="{p}"/><path d="M58 218q60-15 110 18l-29 48q-56-28-110-20z" fill="{s}"/><path d="M57 239l-20 38M85 243l-9 41M114 248l2 40M143 258l15 30" stroke="#24343B" stroke-width="8"/>',
        "mop": f'<path d="M168 28h25v185h-25z" fill="{p}"/><path d="M147 207h68v30h-68z" fill="{s}"/><path d="M160 237l-30 45M180 237v52M200 237l30 45M145 237l-18 32M215 237l18 32" stroke="#24343B" stroke-width="10" stroke-linecap="round"/>',
        "wringer-bucket": f'<path d="M90 105h180l-18 165H108z" fill="{p}"/><path d="M78 89h205v25H78z" fill="{s}"/><path d="M115 90q10-70 130 0" fill="none" stroke="#24343B" stroke-width="13"/><path d="M128 145h105" stroke="#FFFFFF" stroke-width="10"/>',
        "wet-floor-sign": f'<path d="M180 45l120 210H60z" fill="{p}"/><path d="M180 95l65 115H115z" fill="#FFFFFF"/><path d="M180 125v45M180 190v7" stroke="{s}" stroke-width="13" stroke-linecap="round"/>',
        "nitrile-gloves": f'<path d="M102 250l-25-68q-8-22 8-30 17-8 27 13l-17-86q-4-23 15-27 18-4 24 19l12 58-2-83q0-23 19-23 20 0 21 23l4 80 8-72q3-22 21-20 20 2 17 25l-7 81 17-45q9-21 27-12 17 9 7 29l-39 88q-19 43-61 43z" fill="{p}"/><path d="M130 193h90" stroke="{s}" stroke-width="12"/>',
        "cut-resistant-gloves": f'<path d="M102 250l-25-68q-8-22 8-30 17-8 27 13l-17-86q-4-23 15-27 18-4 24 19l12 58-2-83q0-23 19-23 20 0 21 23l4 80 8-72q3-22 21-20 20 2 17 25l-7 81 17-45q9-21 27-12 17 9 7 29l-39 88q-19 43-61 43z" fill="{p}"/><path d="M125 210l96-75M145 230l91-74M110 183l55-42" stroke="{s}" stroke-width="11"/>',
        "apron": f'<path d="M115 65q65 35 130 0l30 208H85z" fill="{p}"/><path d="M130 63q0-45 50-45t50 45" fill="none" stroke="{s}" stroke-width="18"/><path d="M125 170h110v52H125z" fill="#FFFFFF" opacity=".25"/>',
        "fire-extinguisher": f'<rect x="112" y="72" width="136" height="196" rx="42" fill="{p}"/><path d="M150 72V42h70v30M185 42V20h76" fill="none" stroke="#24343B" stroke-width="13" stroke-linecap="round"/><path d="M210 20q75 18 70 78" fill="none" stroke="{s}" stroke-width="13"/><rect x="135" y="137" width="90" height="54" rx="8" fill="#FFFFFF"/><path d="M155 155h50M155 173h36" stroke="{p}" stroke-width="7"/>',
        "first-aid-kit": f'<rect x="65" y="95" width="230" height="165" rx="24" fill="{p}"/><path d="M130 95V65h100v30" fill="none" stroke="#24343B" stroke-width="14"/><path d="M165 130h32v34h35v31h-35v34h-32v-34h-35v-31h35z" fill="{s}"/>',
        "delivery-van": f'<path d="M45 110h175v125H45z" fill="{p}"/><path d="M220 150h65l45 50v35H220z" fill="{s}"/><path d="M235 165h43l30 35h-73z" fill="#F4F7F5"/><circle cx="105" cy="246" r="28" fill="#24343B"/><circle cx="275" cy="246" r="28" fill="#24343B"/><circle cx="105" cy="246" r="12" fill="#F4F7F5"/><circle cx="275" cy="246" r="12" fill="#F4F7F5"/><path d="M75 145h110" stroke="#FFFFFF" stroke-width="11"/>',
    }
    generic = f'<rect x="70" y="55" width="220" height="220" rx="34" fill="{p}"/><circle cx="180" cy="165" r="68" fill="{s}"/><path d="M125 165h110M180 110v110" stroke="#FFFFFF" stroke-width="16" stroke-linecap="round"/>'
    return icons.get(kind, generic)


def wrap_label(value, limit=25):
    words = value.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > limit and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines[:2]


def build_svg(item, index):
    primary = PALETTE[index % len(PALETTE)]
    secondary = "#F28C28" if primary != "#F28C28" else "#087F5B"
    category = html.escape(item["category"])
    name = html.escape(item["name"])
    code = html.escape(item["code"])
    label_lines = wrap_label(item["name"])
    label_text = "".join(
        f'<text x="360" y="{520 + line_no * 38}" text-anchor="middle" font-family="Arial, sans-serif" font-size="27" font-weight="700" fill="#1D3334">{html.escape(line)}</text>'
        for line_no, line in enumerate(label_lines)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="720" viewBox="0 0 720 720">
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F2F8F5"/><stop offset="1" stop-color="#FFF5E8"/></linearGradient><filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#183331" flood-opacity=".14"/></filter></defs>
  <rect width="720" height="720" rx="42" fill="url(#bg)"/>
  <rect x="28" y="28" width="664" height="664" rx="34" fill="#FFFFFF" stroke="#DCE8E2" stroke-width="3" filter="url(#shadow)"/>
  <path d="M62 29h596q34 0 34 34v100H28V63q0-34 34-34z" fill="#073B32"/>
  <circle cx="91" cy="83" r="27" fill="{secondary}"/><path d="M79 83h24M91 71v24" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round"/>
  <text x="133" y="79" font-family="Arial, sans-serif" font-size="27" font-weight="700" fill="#FFFFFF">QUETZALMART</text>
  <text x="133" y="111" font-family="Arial, sans-serif" font-size="17" fill="#B8D8CB">MATERIAL OPERATIVO · {category}</text>
  <text x="648" y="84" text-anchor="end" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="{secondary}">{code}</text>
  <circle cx="360" cy="322" r="158" fill="#F2F7F4"/>
  <circle cx="360" cy="322" r="128" fill="#FFFFFF" stroke="#E6EFEA" stroke-width="3"/>
  <g transform="translate(180 175) scale(1.0)">{icon_markup(item["kind"], primary, secondary)}</g>
  {label_text}
  <text x="360" y="606" text-anchor="middle" font-family="Arial, sans-serif" font-size="17" fill="#59716A">Código interno: {code} · QuetzalMart</text>
  <rect x="178" y="632" width="364" height="40" rx="20" fill="#FFF1E0" stroke="#F3D1A7"/>
  <text x="360" y="658" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#9B4F00">USO INTERNO · NO VENDIBLE</text>
</svg>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--width", type=int, default=720)
    args = parser.parse_args()
    renderer = shutil.which("rsvg-convert")
    if not renderer:
        raise SystemExit("No se encontró rsvg-convert para convertir las ilustraciones SVG a PNG.")
    items = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if len(items) != 60 or len({item["code"] for item in items}) != 60:
        raise SystemExit("El manifiesto debe incluir exactamente 60 códigos internos únicos.")
    args.output.mkdir(parents=True, exist_ok=True)
    for index, item in enumerate(items):
        svg_path = args.output / f'{item["code"]}.svg'
        png_path = args.output / f'{item["code"]}.png'
        svg_path.write_text(build_svg(item, index), encoding="utf-8")
        subprocess.run(
            [renderer, "-w", str(args.width), "-h", str(args.width), "-o", str(png_path), str(svg_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    pngs = list(args.output.glob("QMI-*.png"))
    if len(pngs) != 60 or len({p.stat().st_size for p in pngs}) < 10:
        raise SystemExit("La generación de las 60 imágenes no pasó la validación de cantidad/variedad.")
    print(f"IMAGES_OK count={len(pngs)} output={args.output}")


if __name__ == "__main__":
    main()
