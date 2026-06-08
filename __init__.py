"""LaTeX transform plugin - converts LaTeX math to Unicode for better display."""

import re
from typing import Optional

# Symbol mappings (LaTeX command -> Unicode)
SYMBOLS = {
    # Greek lowercase
    '\\alpha': 'α', '\\beta': 'β', '\\gamma': 'γ', '\\delta': 'δ',
    '\\epsilon': 'ε', '\\varepsilon': 'ε', '\\zeta': 'ζ', '\\eta': 'η',
    '\\theta': 'θ', '\\vartheta': 'ϑ', '\\iota': 'ι', '\\kappa': 'κ',
    '\\lambda': 'λ', '\\mu': 'μ', '\\nu': 'ν', '\\xi': 'ξ',
    '\\pi': 'π', '\\varpi': 'ϖ', '\\rho': 'ρ', '\\varrho': 'ϱ',
    '\\sigma': 'σ', '\\varsigma': 'ς', '\\tau': 'τ', '\\upsilon': 'υ',
    '\\phi': 'φ', '\\varphi': 'φ', '\\chi': 'χ', '\\psi': 'ψ', '\\omega': 'ω',
    
    # Greek uppercase
    '\\Gamma': 'Γ', '\\Delta': 'Δ', '\\Theta': 'Θ', '\\Lambda': 'Λ',
    '\\Xi': 'Ξ', '\\Pi': 'Π', '\\Sigma': 'Σ', '\\Upsilon': 'Υ',
    '\\Phi': 'Φ', '\\Psi': 'Ψ', '\\Omega': 'Ω',
    
    # Big operators
    '\\sum': '∑', '\\prod': '∏', '\\coprod': '∐',
    '\\int': '∫', '\\iint': '∬', '\\iiint': '∭', '\\oint': '∮',
    '\\bigcup': '⋃', '\\bigcap': '⋂', '\\bigvee': '⋁', '\\bigwedge': '⋀',
    '\\bigoplus': '⨁', '\\bigotimes': '⨂',
    
    # Calculus
    '\\partial': '∂', '\\nabla': '∇', '\\sqrt': '√',
    
    # Sets
    '\\emptyset': '∅', '\\varnothing': '∅', '\\infty': '∞',
    '\\in': '∈', '\\notin': '∉', '\\ni': '∋',
    '\\subset': '⊂', '\\supset': '⊃', '\\subseteq': '⊆', '\\supseteq': '⊇',
    '\\subsetneq': '⊊', '\\supsetneq': '⊋',
    '\\sqsubset': 'sq', '\\sqsupset': 'sq', '\\sqsubseteq': '⊑', '\\sqsupseteq': '⊒',
    '\\setminus': '∖',
    
    # Logic
    '\\forall': '∀', '\\exists': '∃', '\\nexists': '∄',
    '\\land': '∧', '\\lor': '∨', '\\lnot': '¬',
    '\\implies': '⟹', '\\impliedby': '⟸', '\\iff': '⟺',
    
    # Relations
    '\\leq': '≤', '\\le': '≤', '\\geq': '≥', '\\ge': '≥',
    '\\neq': '≠', '\\ne': '≠',
    '\\approx': '≈', '\\sim': '∼', '\\simeq': '≃', '\\cong': '≅',
    '\\equiv': '≡', '\\propto': '∝',
    '\\ll': '≪', '\\gg': '≫',
    '\\perp': '⊥', '\\parallel': '∥',
    
    # Arrows
    '\\leftarrow': '←', '\\gets': '←',
    '\\rightarrow': '→', '\\to': '→',
    '\\leftrightarrow': '↔',
    '\\Leftarrow': '⇐', '\\Rightarrow': '⇒', '\\Leftrightarrow': '⇔',
    '\\mapsto': '↦',
    '\\hookrightarrow': '↪', '\\hookleftarrow': '↩',
    '\\uparrow': '↑', '\\downarrow': '↓', '\\updownarrow': '↕',
    '\\Uparrow': '⇑', '\\Downarrow': '⇓', '\\Updownarrow': '⇕',
    '\\nearrow': '↗', '\\searrow': '↘', '\\swarrow': '↙', '\\nwarrow': '↖',
    
    # Misc operators
    '\\pm': '±', '\\mp': '∓',
    '\\times': '×', '\\div': '÷', '\\cdot': '·', '\\ast': '∗', '\\star': '⋆',
    '\\circ': '∘', '\\bullet': '•',
    '\\oplus': '⊕', '\\ominus': '⊖', '\\otimes': '⊗', '\\oslash': '⊘',
    '\\dagger': '†', '\\ddagger': '‡',
    '\\cap': '∩', '\\cup': '∪',
    '\\vee': '∨', '\\wedge': '∧',
    '\\diamond': '⋄', '\\triangle': '△',
    '\\nmid': '∤',
    
    # Dots
    '\\cdots': '⋯', '\\dots': '…', '\\ldots': '…',
    '\\vdots': '⋮', '\\ddots': '⋱',
    
    # Escaped characters
    '\\%': '%', '\\$': '$', '\\&': '&', '\\#': '#', '\\_': '_',
    '\\{': '{', '\\}': '}',
    
    # Misc
    '\\neg': '¬', '\\prime': '′', '\\angle': '∠',
    '\\triangle': '△', '\\triangleright': '▷', '\\triangleleft': '◁',
    '\\star': '⋆', '\\diamond': '⋄',
    '\\ell': 'ℓ', '\\Re': 'ℜ', '\\Im': 'ℑ',
    '\\aleph': 'ℵ', '\\beth': 'ℶ',
    '\\blacksquare': '■', '\\square': '□',
    '\\checkmark': '✓', '\\crossmark': '✗',
    '\\qed': '∎',
    '\\Therefore': 'Therefore', '\\because': 'Because',
}

# Blackboard bold letters
BB = {
    'A': '𝔸', 'B': '𝔹', 'C': 'ℂ', 'D': '𝔻', 'E': '𝔼', 'F': '𝔽',
    'G': '𝔾', 'H': 'ℍ', 'I': '𝕀', 'J': '𝕁', 'K': '𝕂', 'L': '𝕃',
    'M': '𝕄', 'N': 'ℕ', 'O': '𝕆', 'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ',
    'S': '𝕊', 'T': '𝕋', 'U': '𝕌', 'V': '𝕍', 'W': '𝕎', 'X': '𝕏',
    'Y': '𝕐', 'Z': 'ℤ',
}

# Calligraphic letters
CAL = {
    'A': '𝒜', 'B': 'ℬ', 'C': '𝒞', 'D': '𝒟', 'E': 'ℰ', 'F': 'ℱ',
    'G': '𝒢', 'H': 'ℋ', 'I': 'ℐ', 'J': '𝒥', 'K': '𝒦', 'L': 'ℒ',
    'M': 'ℳ', 'N': '𝒩', 'O': '𝒪', 'P': '𝒫', 'Q': '𝒬', 'R': 'ℛ',
    'S': '𝒮', 'T': '𝒯', 'U': '𝒰', 'V': '𝒱', 'W': '𝒲', 'X': '𝒳',
    'Y': '𝒴', 'Z': '𝒵',
}

# Fraktur letters
FRAK = {
    'A': '𝔄', 'B': '𝔅', 'C': 'ℭ', 'D': '𝔇', 'E': '𝔈', 'F': '𝔉',
    'G': '𝔊', 'H': 'ℌ', 'I': 'ℑ', 'J': '𝔍', 'K': '𝔎', 'L': '𝔏',
    'M': '𝔐', 'N': '𝔑', 'O': '𝔒', 'P': '𝔓', 'Q': '𝔔', 'R': 'ℜ',
    'S': '𝔖', 'T': '𝔗', 'U': '𝔘', 'V': '𝔙', 'W': '𝔚', 'X': '𝔛',
    'Y': '𝔜', 'Z': 'ℨ',
}

# Superscript/subscript mappings
SUPERSCRIPT = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    'n': 'ⁿ', 'i': 'ⁱ',
    '+': '⁺', '-': '⁻', '=': '⁼',
}

SUBSCRIPT = {
    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
    '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
    'a': 'ₐ', 'e': 'ₑ', 'i': 'ᵢ', 'j': 'ⱼ',
    'k': 'ₖ', 'l': 'ₗ', 'm': 'ₘ', 'n': 'ₙ',
    'o': 'ₒ', 'p': 'ₚ', 'r': 'ᵣ', 's': 'ₛ',
    't': 'ₜ', 'u': 'ᵤ', 'v': 'ᵥ', 'x': 'ₓ',
    '+': '₊', '-': '₋', '=': '₌',
}


def _convert_script(body: str, mapping: dict, prefix: str) -> str:
    """Convert a script body to Unicode superscript/subscript."""
    result = []
    for ch in body:
        if ch in mapping:
            result.append(mapping[ch])
        else:
            # Can't convert, fall back to raw
            return f"{prefix}{body}"
    return ''.join(result)


def _replace_braced_command(s: str, command: str, replacer) -> str:
    """Replace a braced command like \\command{...} with the result of replacer."""
    pattern = re.compile(re.escape(command) + r'\{([^{}]+)\}')
    return pattern.sub(lambda m: replacer(m.group(1)), s)


def tex_to_unicode(input_str: str) -> str:
    """Convert LaTeX math to Unicode for terminal display."""
    s = input_str
    
    # Math font commands
    s = re.sub(r'\\mathbb\s*\{([A-Za-z])\}', lambda m: BB.get(m.group(1), m.group(0)), s)
    s = re.sub(r'\\mathcal\s*\{([A-Za-z])\}', lambda m: CAL.get(m.group(1), m.group(0)), s)
    s = re.sub(r'\\mathfrak\s*\{([A-Za-z])\}', lambda m: FRAK.get(m.group(1), m.group(0)), s)
    s = re.sub(r'\\mathbf\s*\{([^{}]+)\}', lambda m: m.group(1), s)
    s = re.sub(r'\\mathit\s*\{([^{}]+)\}', lambda m: m.group(1), s)
    s = re.sub(r'\\textit\s*\{([^{}]+)\}', lambda m: m.group(1), s)
    s = re.sub(r'\\mathrm\s*\{([^{}]+)\}', lambda m: m.group(1), s)
    s = re.sub(r'\\text\s*\{([^{}]+)\}', lambda m: m.group(1), s)
    s = re.sub(r'\\operatorname\s*\{([^{}]+)\}', lambda m: m.group(1), s)
    
    # Combining marks
    s = re.sub(r'\\overline\s*\{([^{}]+)\}', lambda m: f"{m.group(1)}\u0305", s)
    s = re.sub(r'\\hat\s*\{([^{}]+)\}', lambda m: f"{m.group(1)}\u0302", s)
    s = re.sub(r'\\bar\s*\{([^{}]+)\}', lambda m: f"{m.group(1)}\u0304", s)
    s = re.sub(r'\\tilde\s*\{([^{}]+)\}', lambda m: f"{m.group(1)}\u0303", s)
    s = re.sub(r'\\vec\s*\{([^{}]+)\}', lambda m: f"{m.group(1)}\u20D7", s)
    s = re.sub(r'\\dot\s*\{([^{}]+)\}', lambda m: f"{m.group(1)}\u0307", s)
    s = re.sub(r'\\ddot\s*\{([^{}]+)\}', lambda m: f"{m.group(1)}\u0308", s)
    
    # Fractions: \frac{a}{b} -> a/b
    def replace_frac(m):
        numerator = m.group(1)
        denominator = m.group(2)
        # Wrap complex expressions in parentheses
        if len(numerator) > 1 and not numerator.startswith('('):
            numerator = f"({numerator})"
        if len(denominator) > 1 and not denominator.startswith('('):
            denominator = f"({denominator})"
        return f"{numerator}/{denominator}"
    
    s = re.sub(r'\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', replace_frac, s)
    
    # \boxed{} and \fbox{} - just extract content
    s = _replace_braced_command(s, '\\boxed', lambda body: body.strip())
    s = _replace_braced_command(s, '\\fbox', lambda body: body.strip())
    
    # Arrows with labels
    s = re.sub(r'\\xrightarrow\s*\{([^{}]*)\}', lambda m: f"─{m.group(1).strip()}→", s)
    s = re.sub(r'\\xleftarrow\s*\{([^{}]*)\}', lambda m: f"←{m.group(1).strip()}─", s)
    s = s.replace('\\Longrightarrow', '⟹')
    s = s.replace('\\Longleftarrow', '⟸')
    s = s.replace('\\Longleftrightarrow', '⟺')
    
    # Modular arithmetic
    s = re.sub(r'\s*\\pmod\s*\{([^{}]*)\}', lambda m: f" (mod {m.group(1).strip()})", s)
    s = re.sub(r'\s*\\pod\s*\{([^{}]*)\}', lambda m: f" ({m.group(1).strip()})", s)
    s = re.sub(r'\s*\\tag\s*\{([^{}]*)\}', lambda m: f" ({m.group(1).strip()})", s)
    
    # Size wrappers - strip them
    s = re.sub(r'\\(?:Bigg|bigg|Big|big)[lrm]?(?![A-Za-z])', '', s)
    
    # Style hints
    s = re.sub(r'\\(?:scriptscriptstyle|displaystyle|scriptstyle|textstyle|nolimits|limits)(?![A-Za-z])\s*', '', s)
    
    # \left and \right
    s = re.sub(r'\\left(?![A-Za-z])\.?', '', s)
    s = re.sub(r'\\right(?![A-Za-z])\.?', '', s)
    
    # Symbol substitution - punctuation first (can be followed by letters)
    s = re.sub(r'\\(?:[{}|,;:!%])', lambda m: SYMBOLS.get(m.group(0), m.group(0)), s)
    # Then letter commands
    s = re.sub(r'\\[a-zA-Z]+', lambda m: SYMBOLS.get(m.group(0), m.group(0)), s)
    
    # Superscripts: ^{...} or ^c
    def replace_superscript(m):
        return _convert_script(m.group(1), SUPERSCRIPT, '^')
    
    s = re.sub(r'\^\s*\{([^{}]+)\}', replace_superscript, s)
    s = re.sub(r'\^([A-Za-z0-9+\-=])', lambda m: SUPERSCRIPT.get(m.group(1), m.group(0)), s)
    
    # Subscripts: _{...} or _c
    def replace_subscript(m):
        return _convert_script(m.group(1), SUBSCRIPT, '_')
    
    s = re.sub(r'_\s*\{([^{}]+)\}', replace_subscript, s)
    s = re.sub(r'_([A-Za-z0-9+\-=])', lambda m: SUBSCRIPT.get(m.group(1), m.group(0)), s)
    
    return s


def transform_latex(response_text: str, **kwargs) -> Optional[str]:
    """Transform LaTeX math formulas in the response to Unicode.
    
    This hook intercepts LLM responses and converts LaTeX math
    to Unicode for better display in messaging platforms.
    """
    if not response_text:
        return None
    
    # Pattern to match LaTeX math blocks: $$...$$ or \[...\]
    def replace_display_math(m):
        content = m.group(1).strip()
        return tex_to_unicode(content)
    
    # Pattern to match inline math: $...$ or \(...\)
    def replace_inline_math(m):
        content = m.group(1).strip()
        return tex_to_unicode(content)
    
    result = response_text
    
    # Replace display math blocks first ($$...$$ and \[...\])
    result = re.sub(r'\$\$(.+?)\$\$', replace_display_math, result, flags=re.DOTALL)
    result = re.sub(r'\\\[(.+?)\\\]', replace_display_math, result, flags=re.DOTALL)
    
    # Replace inline math ($...$ and \(...\))
    # Be careful not to match $$ as $
    result = re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', replace_inline_math, result)
    result = re.sub(r'\\\((.+?)\\\)', replace_inline_math, result)
    
    return result if result != response_text else None


def register(ctx):
    """Register the LaTeX transform hook."""
    ctx.register_hook("transform_llm_output", transform_latex)
