"""
Text rendering utilities for PDF creation.

Handles rendering text in various formats and styles for PDF documents.
"""

import re

from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch
from io import BytesIO


class TextRenderer:
    """
    Class to help with text rendering in PDFs.
    
    This class provides methods to render text with various styles
    in a PDF document.
    """
    
    def __init__(self, colors):
        """
        Initialize the text renderer with the color scheme.
        
        Args:
            colors: Dictionary of colors to use for rendering
        """
        self.colors = colors
        self.styles = getSampleStyleSheet()
        
        # Determine if we're using a dark theme based on the background color
        self.is_dark_theme = False
        if "background" in colors:
            bg_color = colors["background"]
            # Check if it's a tuple of RGB values
            if isinstance(bg_color, tuple) and len(bg_color) >= 3:
                # If the average RGB value is less than 0.5, it's a dark theme
                avg_value = sum(bg_color[:3]) / 3
                if avg_value < 0.5:
                    self.is_dark_theme = True
        
        # Improved IDE-style color schemes for different code elements with more vibrant colors
        # Make colors more vibrant for better visibility in PDF
        self.code_colors = {
            "keyword": (0.0, 0.0, 1.0),      # Bright Blue for keywords
            "decorator": (0.7, 0.0, 0.7),    # Bright Purple for decorators
            "function": (1.0, 0.4, 0.0),     # Bright Orange for functions
            "string": (0.0, 0.7, 0.0),       # Bright Green for strings
            "number": (1.0, 0.0, 0.0),       # Bright Red for numbers
            "comment": (0.5, 0.5, 0.5),      # Gray for comments
            "type": (0.0, 0.6, 0.6),         # Bright Teal for types
            "command": (0.7, 0.4, 0.0),      # Bright Brown for commands
            "default": (0.0, 0.0, 0.0),      # Black for other code
        }
        
        # For dark theme, adjust the code colors for better contrast
        if self.is_dark_theme:
            self.code_colors = {
                "keyword": (0.4, 0.4, 1.0),      # Lighter Blue for keywords
                "decorator": (0.9, 0.4, 0.9),    # Lighter Purple for decorators
                "function": (1.0, 0.6, 0.2),     # Lighter Orange for functions
                "string": (0.4, 0.9, 0.4),       # Lighter Green for strings
                "number": (1.0, 0.4, 0.4),       # Lighter Red for numbers
                "comment": (0.7, 0.7, 0.7),      # Lighter Gray for comments
                "type": (0.4, 0.8, 0.8),         # Lighter Teal for types
                "command": (0.9, 0.6, 0.2),      # Lighter Brown for commands
                "default": (0.9, 0.9, 0.9),      # Off-white for other code
            }
        
        # Technical terms to highlight with their categories
        self.tech_terms = self._init_tech_terms()
        # Sort terms by length (longest first) to avoid partial matches
        self.sorted_terms = sorted(self.tech_terms.keys(), key=len, reverse=True)
        
        # Add common keywords that should NOT be highlighted when they appear as part of normal text
        self.exclude_standalone = {
            "for", "while", "if", "in", "of", "on", "at", "to", "by", "is", "are", "was", "were", 
            "the", "a", "an", "and", "or", "but", "not", "with", "without", "from", "into", "onto",
            "over", "under", "above", "below", "between", "among", "through", "across", "around",
            "about", "against", "along", "before", "after", "during", "since", "until", "till",
            "up", "down", "out", "off", "away", "back", "forward", "together", "apart", "aside",
            "as", "like", "than", "that", "this", "these", "those", "which", "who", "whom", "whose",
            "what", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
            "most", "other", "some", "such", "no", "nor", "neither", "either", "whether", "yet",
            "so", "then", "too", "very", "can", "will", "just", "don", "should", "now",
        }
    
    def draw_paragraph(self, canvas, text, style, x, y, width, height=None):
        """
        Draw a paragraph of text on the canvas.
        
        Args:
            canvas: The ReportLab canvas to draw on
            text: The text to draw
            style: The ParagraphStyle to use
            x: The x-coordinate for the left edge of the paragraph
            y: The y-coordinate for the top edge of the paragraph
            width: The width of the paragraph
            height: Optional height constraint for the paragraph
        
        Returns:
            The height of the rendered paragraph
        """
        p = Paragraph(text, style)
        w, h = p.wrap(width, 1000)  # 1000 is arbitrarily large
        
        if height is None:
            height = h
        
        p.drawOn(canvas, x, y - h)
        return h

    def _init_tech_terms(self):
        """Initialize the technical terms dictionary"""
        tech_terms = {
            # Keywords and language features
            "async": "keyword",
            "await": "keyword",
            "import": "keyword",
            "export": "keyword",
            "function": "keyword",
            "class": "keyword",
            "const": "keyword",
            "let": "keyword",
            "var": "keyword",
            "return": "keyword",
            "if": "keyword",
            "else": "keyword",
            "for": "keyword",
            "while": "keyword",
            "switch": "keyword",
            "case": "keyword",
            "try": "keyword",
            "catch": "keyword",
            "finally": "keyword",
            "new": "keyword",
            "super": "keyword",
            "extends": "keyword",
            "implements": "keyword",
            # Next.js specific data fetching methods
            "getStaticProps": "function",
            "getServerSideProps": "function",
            "getStaticPaths": "function",
            "getInitialProps": "function",
            "useEffect": "function",
            "useState": "function",
            "useRouter": "function",
            "useSWR": "function",
            "client-side": "default",
            "server-side": "default",
            # Types
            "string": "type",
            "number": "type",
            "boolean": "type",
            "object": "type",
            "array": "type",
            "null": "type",
            "undefined": "type",
            "void": "type",
            "any": "type",
            "never": "type",
            "interface": "type",
            "type": "type",
            "JavaScript": "type",
            "TypeScript": "type",
            "Python": "type",
            "Java": "type",
            "C++": "type",
            "C#": "type",
            "Ruby": "type",
            "Go": "type",
            "PHP": "type",
            # Functions and methods
            "useState": "function",
            "useEffect": "function",
            "useContext": "function",
            "useReducer": "function",
            "useCallback": "function",
            "useMemo": "function",
            "useRef": "function",
            "render": "function",
            "componentDidMount": "function",
            "componentDidUpdate": "function",
            "constructor": "function",
            "fetch": "function",
            "map": "function",
            "reduce": "function",
            "forEach": "function",
            "push": "function",
            "pop": "function",
            "shift": "function",
            "unshift": "function",
            # Frameworks and libraries
            "Next.js": "default",
            "React": "default",
            "Node.js": "default",
            "Express": "default",
            "Vue": "default",
            "Angular": "default",
            "jQuery": "default",
            "Redux": "default",
            "GraphQL": "default",
            "REST": "default",
            "API": "default",
            "JWT": "default",
            "OAuth": "default",
            "Firebase": "default",
            "MongoDB": "default",
            "PostgreSQL": "default",
            "MySQL": "default",
            "SSR": "default",
            "SSG": "default",
            "ISR": "default",
            "CSR": "default",
            "SPA": "default",
            "PWA": "default",
            # File paths and patterns
            "pages/api": "string",
            "/api/": "string",
            "[id].js": "string",
            "[...slug].js": "string",
            "404.js": "string",
            "_app.js": "string",
            "_document.js": "string",
            "middleware.js": "string",
            # HTTP methods
            "GET": "keyword",
            "POST": "keyword",
            "PUT": "keyword",
            "DELETE": "keyword",
            "PATCH": "keyword",
            # Backend & Programming Languages
            "PHP": "type",
            "Python": "type",
            "JavaScript": "type",
            "C++": "type",
            "Bash": "type",
            # PHP Frameworks
            "Laravel": "default",
            "Symfony": "default",
            "Zend": "default",
            # Frontend Core
            "HTML5": "type",
            "CSS3": "type",
            "Sass": "type",
            # Frontend Frameworks & Libraries
            "Vue.js": "default",
            "Angular": "default",
            # CSS Frameworks
            "TailwindCSS": "default",
            "Bootstrap": "default",
            # Cloud Platforms
            "AWS": "default",
            "GCP": "default",
            "Azure": "default",
            "DigitalOcean": "default",
            # DevOps & Infrastructure
            "Docker": "default",
            "Kubernetes": "default",
            "Terraform": "default",
            "Puppet": "default",
            # Kubernetes Core Components
            "Control Plane": "default",
            "control plane": "default",
            "Control plane": "default",
            "API Server": "default",
            "api server": "default",
            "API server": "default",
            "Controller Manager": "default",
            "controller manager": "default",
            "Controller manager": "default",
            "Scheduler": "default",
            "scheduler": "default",
            "etcd": "default",
            # Kubernetes Node Components
            "Nodes": "default",
            "nodes": "default",
            "Node": "default",
            "node": "default",
            "Kubelet": "default",
            "kubelet": "default",
            "Kube Proxy": "default",
            "kube proxy": "default",
            "Kube proxy": "default",
            "Container Runtime": "default",
            "container runtime": "default",
            "Container runtime": "default",
            # Kubernetes Features and Operations
            "Service Discovery": "default",
            "service discovery": "default",
            "Service discovery": "default",
            "Scaling": "default",
            "scaling": "default",
            "Rolling Updates": "default",
            "rolling updates": "default",
            "Rolling updates": "default",
            # Add variations of the terms to ensure proper matching
            "control plane": "default",
            "api server": "default",
            "controller manager": "default",
            "kube proxy": "default",
            "container runtime": "default",
            # Other Kubernetes Resources
            "Pod": "default",
            "Deployment": "default",
            "Service": "default",
            "Ingress": "default",
            "ReplicaSet": "default",
            "StatefulSet": "default",
            "Job": "default",
            "CronJob": "default",
            "Namespace": "default",
            # Web Servers & Load Balancers
            "NGINX": "default",
            "Apache": "default",
            "Traefik": "default",
            # Databases & Caching
            "Redis": "default",
            "Elasticsearch": "default",
            "Cassandra": "default",
            # CI/CD & Version Control
            "Git": "default",
            "GitHub": "default",
            "GitLab": "default",
            "Jenkins": "default",
            # Operating Systems & Runtime
            "Linux": "default",
            # CMS
            "WordPress": "default",
            # Command-line specific terms and services
            "find": "command",
            "DHCP": "type",
            "isc-dhcp-server": "command",
            "systemctl": "command",
            "start": "command",
            "enable": "command",
            "service": "default",
            "daemon": "default",
        }

        # Add command patterns that should be matched as whole phrases
        self.command_patterns = [
            r"«CMD»([^«]+?)«/CMD»",  # More restrictive CMD pattern - must be first
            r"'\s*(systemctl\s+(?:start|stop|enable|disable|status)\s+[\w\-\.]+)\s*'",
            r"'\s*(ps\s+aux)\s*'",
            r"'\s*(ps)\s*'",
            r"'\s*(kill\s+-9\s+\d+)\s*'",
            r"'\s*(kill\s+\d+)\s*'",
            r"'\s*(pgrep\s+[\w\-\.]+)\s*'",
            r"'\s*(pkill\s+[\w\-\.]+)\s*'",
            r"'\s*(valgrind\s+--leak-check=full\s+\./[\w\-\.]+)\s*'",
            r"'\s*(ps\s+[\-a-zA-Z]+)\s*'",
        ]

        # Add more common terms with default styling
        common_terms = [
            "component",
            "props",
            "state",
            "hooks",
            "routing",
            "Link",
            "Image",
            "Head",
            "next/router",
            "next/image",
            "API routes",
            "file-based routing",
            "middleware",
            "callback",
            "promise",
            "closure",
            "prototype",
            "hoisting",
            "event loop",
            "DOM",
            "virtual DOM",
            "JSX",
            "TSX",
            "ES6",
            "async/await",
            "Promise",
            "frontend",
            "backend",
            "full-stack",
            "deployment",
            "production",
            "development",
            "testing",
            "CI/CD pipeline",
            "containerization",
            "microservices",
            "serverless",
            "authentication",
            "load balancing",
            "caching",
            "indexing",
            "query",
            "migration",
            "ORM",
            "REST API",
            "endpoint",
            "request",
            "response",
            "middleware",
            "controller",
            "model",
            "view",
            "MVC",
            "MVVM",
            "state management",
            "hooks",
            "components",
            "responsive design",
            "mobile-first",
            "accessibility",
            "SEO",
            "analytics",
        ]

        for term in common_terms:
            if term not in tech_terms:
                tech_terms[term] = "default"

        return tech_terms

    def _clean_text(self, text):
        """Remove all existing markers and normalize the text"""
        # Remove all existing markers while preserving original text
        cleaned = re.sub(
            r"«(?:CMD|TECH)»(.*?)«/(?:CMD|TECH)»", lambda m: m.group(1).strip(), text
        )

        # Handle different text types differently
        if any(indicator in cleaned for indicator in ["25%", "50%", "75%"]):
            # Don't normalize whitespace for progress indicators
            return cleaned
        elif "```" in cleaned:
            # Split by code blocks and process each part
            parts = cleaned.split("```")
            for i in range(len(parts)):
                if i % 2 == 0:  # Not a code block
                    parts[i] = re.sub(r"\s+", " ", parts[i])
            return "```".join(parts)
        else:
            # Normal text normalization
            return re.sub(r"\s+", " ", cleaned)

    def draw_text_with_highlights(self, c, text, x, y, width, font_name, font_size, text_color):
        """Draw text with syntax highlighting for code blocks and technical terms"""
        # Initialize variables to track our position
        current_y = y
        
        # Regular expression to identify inline code
        inline_code_pattern = r'`([^`]+)`'
        has_inline_code = re.search(inline_code_pattern, text) is not None
        
        # Check for triple backtick code blocks first
        if '```' in text:
            # Split text into regular text and code blocks
            parts = []
            i = 0
            
            # Process triple backtick code blocks
            while i < len(text):
                # Look for triple backticks
                if text[i:i+3] == '```' and i+3 < len(text):
                    # Find the end of this code block
                    start_index = i
                    i += 3
                    
                    # Skip language identifier if present (e.g., ```python)
                    language = ""
                    lang_start = i
                    while i < len(text) and text[i] != '\n' and i < start_index + 20:
                        i += 1
                    
                    # Capture the language if specified
                    if i > lang_start:
                        language = text[lang_start:i].strip().lower()
                    
                    # Find the closing triple backticks
                    end_marker = text.find('```', i)
                    if end_marker == -1:
                        # No closing marker, treat the rest as code
                        end_marker = len(text)
                    
                    # Add the text before this code block
                    if start_index > 0:
                        parts.append(('text', text[:start_index]))
                    
                    # Add the code block content (without the backticks)
                    code_content = text[i:end_marker].strip()
                    parts.append(('code_block', code_content, language))
                    
                    # Continue from after the end marker
                    if end_marker + 3 < len(text):
                        text = text[end_marker + 3:]
                        i = 0
                    else:
                        # We've reached the end
                        text = ""
                        i = 0
                else:
                    i += 1
            
            # Add any remaining text
            if text:
                parts.append(('text', text))
            
            # Process each part
            for part in parts:
                part_type = part[0]
                part_text = part[1]
                
                if part_type == 'code_block':
                    # Set monospace font for code block
                    c.setFont("Courier", font_size)
                    
                    # Process the code block content
                    code_lines = part_text.split('\n')
                    line_height = font_size * 1.2
                    
                    # Calculate the height of the code block
                    code_block_height = len(code_lines) * line_height
                    
                    # No background for code blocks anymore - just increase spacing
                    padding_top = 10
                    padding_bottom = 15  # Extra padding at bottom to ensure separation from following text
                    
                    # Get language if available (for syntax highlighting)
                    language = part[2] if len(part) > 2 else ""
                    
                    # Draw each line of code with syntax highlighting
                    line_y = current_y - padding_top/2  # Adjust starting position
                    
                    for line in code_lines:
                        # Apply syntax highlighting based on language
                        if language == "python":
                            self._highlight_python_code(c, line, x, line_y, font_size)
                        elif language == "php":
                            self._highlight_php_code(c, line, x, line_y, font_size)
                        else:
                            # Default code coloring
                            c.setFillColorRGB(*self.code_colors["default"])
                            c.drawString(x, line_y, line)
                        line_y -= line_height
                    
                    # Update the current y position
                    current_y = line_y - padding_bottom/2  # Extra space after code block to ensure separation
                
                else:
                    # Process regular text, but check for inline code within it
                    if '`' in part_text:
                        # Process text with inline code blocks
                        self._draw_text_with_inline_code(c, part_text, x, current_y, width, font_name, font_size, text_color)
                        # Calculate approximately how many lines the text took
                        line_count = max(1, len(part_text) // 60)  # rough estimate
                        current_y -= font_size * 1.5 * line_count
                    else:
                        # Draw regular text without inline code
                        c.setFont(font_name, font_size)
                        c.setFillColorRGB(*text_color)
                        
                        # Word-wrap text
                        wrapped_lines = self._wrap_text(part_text, c, font_name, font_size, width)
                        for line in wrapped_lines:
                            c.drawString(x, current_y, line)
                            current_y -= font_size * 1.5  # Increased line spacing to match code blocks
        
        # Handle case where we only have inline code blocks (no triple backticks)
        elif has_inline_code:
            # Process text with inline code blocks
            current_y = self._draw_text_with_inline_code(c, text, x, current_y, width, font_name, font_size, text_color)
        
        # Handle plain text with no code blocks
        else:
            c.setFont(font_name, font_size)
            c.setFillColorRGB(*text_color)
            
            # Word-wrap text
            wrapped_lines = self._wrap_text(text, c, font_name, font_size, width)
            for line in wrapped_lines:
                c.drawString(x, current_y, line)
                current_y -= font_size * 1.5  # Increased line spacing to match code blocks
        
        return current_y

    def _identify_php_syntax(self, text):
        """Identify PHP syntax elements and return the appropriate color"""
        # PHP operators and comparison
        if text in ("==", "===", "!=", "!==", "<", ">", "<=", ">=", "=>", "<=>", 
                   "&&", "||", "!", "and", "or", "xor", "?:", "??", ".", "+", "-", "*", "/", "%", "**"):
            return self.code_colors["keyword"]
        
        # PHP variables
        elif text.startswith("$"):
            return self.code_colors["function"]
        
        # PHP keywords
        elif text in ("if", "else", "elseif", "while", "do", "for", "foreach", "break", 
                     "continue", "switch", "case", "default", "return", "function", 
                     "class", "interface", "trait", "public", "private", "protected",
                     "static", "final", "abstract", "const", "global", "echo", "print",
                     "include", "require", "include_once", "require_once", "namespace",
                     "use", "as", "implements", "extends", "new", "clone", "yield", "throw"):
            return self.code_colors["keyword"]
        
        # SQL keywords
        elif text.upper() in ("SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE", "JOIN", "LEFT", "RIGHT", "INNER", 
                             "OUTER", "FULL", "GROUP", "ORDER", "BY", "HAVING", "LIMIT", "OFFSET", "CREATE", "ALTER", 
                             "DROP", "TABLE", "INDEX", "VIEW", "DATABASE", "FOREIGN", "KEY", "CONSTRAINT", "PRIMARY", 
                             "REFERENCES", "CASCADE", "RESTRICT", "SET", "NULL", "NOT", "DEFAULT", "AUTO_INCREMENT", 
                             "ENGINE", "CHARSET", "COLLATE", "UNIQUE", "AND", "OR", "IN", "BETWEEN", "LIKE", "DESC", 
                             "ASC", "COUNT", "SUM", "AVG", "MIN", "MAX", "DISTINCT", "AS", "ON", "UNION", "ALL", "INTO",
                             "VALUES", "ADD"):
            return self.code_colors["keyword"]
            
        # PHP literals/constants
        elif text in ("true", "false", "null", "TRUE", "FALSE", "NULL") or text.isdigit():
            return self.code_colors["number"]
        
        # PHP strings
        elif (text.startswith("'") and text.endswith("'")) or (text.startswith('"') and text.endswith('"')):
            return self.code_colors["string"]
            
        # PHP built-in functions and MySQL functions
        elif text in ("array", "isset", "empty", "unset", "count", "strlen", "strpos", 
                     "str_replace", "explode", "implode", "json_encode", "json_decode",
                     "date", "time", "mysqli_connect", "mysqli_query", "PDO", "print_r",
                     "var_dump", "die", "exit",
                     "mysqli", "mysql_connect", "mysql_query", "fetch_assoc", "fetch_array"):
            return self.code_colors["function"]
            
        # Default for other elements
        else:
            return self.code_colors["default"]

    def _draw_text_with_inline_code(self, c, text, x, y, width, font_name, font_size, text_color):
        """Draw text that contains inline code blocks (surrounded by single backticks)"""
        # Create a pattern to find inline code
        inline_code_pattern = r'`([^`]+)`'
        
        # Split the text by inline code blocks
        segments = []
        last_end = 0
        
        for match in re.finditer(inline_code_pattern, text):
            start, end = match.span()
            if start > last_end:
                # Add the text before this code block
                segments.append(('text', text[last_end:start]))
            # Add the inline code (without the backticks)
            segments.append(('inline_code', match.group(1)))
            last_end = end
        
        # Add any remaining text
        if last_end < len(text):
            segments.append(('text', text[last_end:]))
        
        # Prepare to wrap text
        wrapped_segments = []
        current_line_width = 0
        current_line = []
        max_line_width = width * 0.95  # Leave a small margin
        
        # Process each segment
        for segment_type, segment_text in segments:
            if segment_type == 'text':
                # Regular text - split into words and add them
                c.setFont(font_name, font_size)
                words = segment_text.split()
                
                for word in words:
                    word_with_space = word + ' '
                    word_width = c.stringWidth(word_with_space, font_name, font_size)
                    
                    # Check if adding this word would exceed line width
                    if current_line_width + word_width > max_line_width:
                        # Complete current line and start a new one
                        if current_line:
                            wrapped_segments.append(current_line)
                            current_line = []
                            current_line_width = 0
                    
                    # Add word to current line
                    current_line.append(('text', word_with_space))
                    current_line_width += word_width
            
            else:  # inline_code
                # Set font for measurement
                c.setFont('Courier', font_size)
                code_width = c.stringWidth(segment_text, 'Courier', font_size)
                
                # If the code is short enough to fit on the current line
                if current_line_width + code_width <= max_line_width:
                    current_line.append(('inline_code', segment_text))
                    current_line_width += code_width
                    
                    # Add a space after the code
                    c.setFont(font_name, font_size)
                    space_width = c.stringWidth(' ', font_name, font_size)
                    current_line.append(('text', ' '))
                    current_line_width += space_width
                else:
                    # Code won't fit on current line
                    
                    # First, save the current line if it's not empty
                    if current_line:
                        wrapped_segments.append(current_line)
                        current_line = []
                        current_line_width = 0
                    
                    # Now handle the code segment
                    # If the entire code is too long for a single line, we need to break it up
                    if code_width > max_line_width:
                        # Break the code into chunks that will fit
                        remaining_code = segment_text
                        
                        while remaining_code:
                            # Find how many characters will fit on this line
                            chars_that_fit = 1  # Always take at least one character
                            
                            for i in range(1, len(remaining_code) + 1):
                                test_width = c.stringWidth(remaining_code[:i], 'Courier', font_size)
                                if test_width > max_line_width:
                                    break
                                chars_that_fit = i
                            
                            # Extract the chunk that fits
                            code_chunk = remaining_code[:chars_that_fit]
                            remaining_code = remaining_code[chars_that_fit:]
                            
                            # Add this chunk as a complete line
                            wrapped_segments.append([('inline_code', code_chunk)])
                            
                            # If there's more code, continue to next line
                            if remaining_code and len(remaining_code.strip()) > 0:
                                # Start fresh for next chunk
                                current_line = []
                                current_line_width = 0
                    else:
                        # Code fits on a line by itself
                        current_line.append(('inline_code', segment_text))
                        current_line_width += code_width
                        
                        # Add a space after the code
                        c.setFont(font_name, font_size)
                        space_width = c.stringWidth(' ', font_name, font_size)
                        current_line.append(('text', ' '))
                        current_line_width += space_width
        
        # Add the last line if not empty
        if current_line:
            wrapped_segments.append(current_line)
        
        # Now draw all the wrapped segments
        current_y = y
        
        for line in wrapped_segments:
            current_x = x
            
            for segment_type, segment_text in line:
                if segment_type == 'inline_code':
                    # Draw code with syntax highlighting (no background)
                    c.setFont('Courier', font_size)
                    code_width = c.stringWidth(segment_text, 'Courier', font_size)
                    
                    # Save state
                    c.saveState()
                    
                    # Get appropriate color for syntax
                    code_text_color = self._identify_php_syntax(segment_text)
                    c.setFillColorRGB(*code_text_color)
                    
                    # Draw the code
                    c.drawString(current_x, current_y, segment_text)
                    
                    # Restore state
                    c.restoreState()
                    
                    # Update position
                    current_x += code_width
                else:
                    # Regular text
                    c.setFont(font_name, font_size)
                    c.setFillColorRGB(*text_color)
                    c.drawString(current_x, current_y, segment_text)
                    
                    # Update position
                    current_x += c.stringWidth(segment_text, font_name, font_size)
            
            # Move to next line
            current_y -= font_size * 1.5  # Increased line spacing to avoid overlap with code blocks
        
        return current_y

    def _highlight_python_code(self, c, line, x, y, font_size):
        """Apply syntax highlighting for Python code"""
        # Define regex patterns for Python syntax elements
        patterns = {
            "keyword": r'\b(def|class|import|from|as|if|elif|else|try|except|finally|with|return|yield|break|continue|pass|raise|assert|for|while|in|is|not|and|or|True|False|None|lambda|global|nonlocal)\b',
            "decorator": r'(@[\w\.]+)',
            "function": r'(?<=def\s)(\w+)(?=\s*\()',
            "string": r'(".*?")|(\'.*?\')',
            "number": r'\b(\d+\.?\d*)\b',
            "comment": r'(#.*)$',
        }
        
        # If the line is empty, just return
        if not line.strip():
            return
        
        # Count leading spaces to preserve indentation
        leading_spaces = len(line) - len(line.lstrip())
        if leading_spaces > 0:
            # Draw the indentation spaces
            c.setFillColorRGB(*self.code_colors["default"])
            spaces = ' ' * leading_spaces
            c.drawString(x, y, spaces)
            x += c.stringWidth(spaces, "Courier", font_size)
            # Remove the leading spaces from the line
            line = line[leading_spaces:]
        
        # Start position for the current segment
        current_x = x
        
        # Check for whole-line comments first
        if line.lstrip().startswith('#'):
            c.setFillColorRGB(*self.code_colors["comment"])
            c.drawString(current_x, y, line)
            return
        
        # Split the line into segments based on syntax patterns
        segments = []
        remaining = line
        
        # Check for strings - these take precedence over other patterns
        in_string = False
        string_start = 0
        
        for i, char in enumerate(remaining):
            if char in ('"', "'") and (i == 0 or remaining[i-1] != '\\'):
                if not in_string:
                    # Start of string
                    if i > 0:
                        segments.append(("normal", remaining[:i]))
                    string_start = i
                    in_string = True
                else:
                    # End of string if it's the same quote type
                    if in_string and char == remaining[string_start]:
                        segments.append(("string", remaining[string_start:i+1]))
                        remaining = remaining[i+1:]
                        in_string = False
                        break
        
        if not in_string:
            # Process the rest of the line for other syntax elements
            for syntax_type, pattern in patterns.items():
                if syntax_type not in ["string"]:  # Already handled strings
                    matches = re.finditer(pattern, remaining)
                    for match in matches:
                        start, end = match.span()
                        if start > 0:
                            segments.append(("normal", remaining[:start]))
                        segments.append((syntax_type, match.group()))
                        remaining = remaining[end:]
                        break  # Process one match at a time
        
        # Add any remaining text
        if remaining:
            segments.append(("normal", remaining))
        
        # If no segments were created, treat the whole line as normal text
        if not segments:
            segments.append(("normal", line))
        
        # Draw each segment with appropriate color
        for segment_type, segment_text in segments:
            if segment_type == "keyword":
                c.setFillColorRGB(*self.code_colors["keyword"])
            elif segment_type == "decorator":
                c.setFillColorRGB(*self.code_colors["decorator"])
            elif segment_type == "function":
                c.setFillColorRGB(*self.code_colors["function"])
            elif segment_type == "string":
                c.setFillColorRGB(*self.code_colors["string"])
            elif segment_type == "number":
                c.setFillColorRGB(*self.code_colors["number"])
            elif segment_type == "comment":
                c.setFillColorRGB(*self.code_colors["comment"])
            else:
                c.setFillColorRGB(*self.code_colors["default"])
            
            # Draw the segment
            c.drawString(current_x, y, segment_text)
            
            # Update the current position
            current_x += c.stringWidth(segment_text, "Courier", font_size)

    def _highlight_php_code(self, c, line, x, y, font_size):
        """Apply syntax highlighting for PHP code"""
        # Define regex patterns for PHP syntax elements
        patterns = {
            "comment": r'(//.*$|#.*$)',
            "variable": r'(\$\w+)',
            "string": r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')',
            "keyword": r'\b(if|else|elseif|while|do|for|foreach|break|continue|switch|case|default|return|function|' + 
                      r'class|interface|trait|public|private|protected|static|final|abstract|const|global|echo|print|' + 
                      r'include|require|include_once|require_once|namespace|use|as|implements|extends|new|clone|yield|throw|' + 
                      r'try|catch|finally|array|list|and|or|xor|isset|empty|unset|exit|die)\b',
            "number": r'\b(\d+\.?\d*)\b',
            "function": r'(\w+)\s*\(',
            "php_tags": r'(<\?php|\?>)',
        }
        
        # If the line is empty, just return
        if not line.strip():
            return
        
        # Count leading spaces to preserve indentation
        leading_spaces = len(line) - len(line.lstrip())
        if leading_spaces > 0:
            # Draw the indentation spaces
            c.setFillColorRGB(*self.code_colors["default"])
            spaces = ' ' * leading_spaces
            c.drawString(x, y, spaces)
            x += c.stringWidth(spaces, "Courier", font_size)
            # Remove the leading spaces from the line
            line = line[leading_spaces:]
        
        # Check for whole-line comments first
        if line.lstrip().startswith('//') or line.lstrip().startswith('#'):
            c.setFillColorRGB(*self.code_colors["comment"])
            c.drawString(x, y, line)
            return
        
        # Initialize current position
        current_x = x
        
        # Apply syntax highlighting using regex patterns
        remaining_line = line
        while remaining_line:
            match_found = False
            
            # Check for comments first
            comment_match = re.search(patterns["comment"], remaining_line)
            if comment_match and comment_match.start() == 0:
                match_found = True
                c.setFillColorRGB(*self.code_colors["comment"])
                comment = comment_match.group(0)
                c.drawString(current_x, y, comment)
                current_x += c.stringWidth(comment, "Courier", font_size)
                remaining_line = remaining_line[len(comment):]
                continue
            
            # Check for strings
            string_match = re.search(patterns["string"], remaining_line)
            if string_match and string_match.start() == 0:
                match_found = True
                c.setFillColorRGB(*self.code_colors["string"])
                string = string_match.group(0)
                c.drawString(current_x, y, string)
                current_x += c.stringWidth(string, "Courier", font_size)
                remaining_line = remaining_line[len(string):]
                continue
                
            # Check for PHP tags
            php_tag_match = re.search(patterns["php_tags"], remaining_line)
            if php_tag_match and php_tag_match.start() == 0:
                match_found = True
                c.setFillColorRGB(*self.code_colors["keyword"])
                php_tag = php_tag_match.group(0)
                c.drawString(current_x, y, php_tag)
                current_x += c.stringWidth(php_tag, "Courier", font_size)
                remaining_line = remaining_line[len(php_tag):]
                continue
            
            # Check for variables
            var_match = re.search(patterns["variable"], remaining_line)
            if var_match and var_match.start() == 0:
                match_found = True
                c.setFillColorRGB(*self.code_colors["function"])
                var = var_match.group(0)
                c.drawString(current_x, y, var)
                current_x += c.stringWidth(var, "Courier", font_size)
                remaining_line = remaining_line[len(var):]
                continue
            
            # Check for keywords
            keyword_match = re.search(patterns["keyword"], remaining_line)
            if keyword_match and keyword_match.start() == 0:
                match_found = True
                c.setFillColorRGB(*self.code_colors["keyword"])
                keyword = keyword_match.group(0)
                c.drawString(current_x, y, keyword)
                current_x += c.stringWidth(keyword, "Courier", font_size)
                remaining_line = remaining_line[len(keyword):]
                continue
            
            # Check for numbers
            number_match = re.search(patterns["number"], remaining_line)
            if number_match and number_match.start() == 0:
                match_found = True
                c.setFillColorRGB(*self.code_colors["number"])
                number = number_match.group(0)
                c.drawString(current_x, y, number)
                current_x += c.stringWidth(number, "Courier", font_size)
                remaining_line = remaining_line[len(number):]
                continue
            
            # Check for function calls
            function_match = re.search(patterns["function"], remaining_line)
            if function_match and function_match.start() == 0:
                match_found = True
                # Keep just the function name
                func_name = function_match.group(1)
                paren = remaining_line[len(func_name)]
                
                # Draw function name
                c.setFillColorRGB(*self.code_colors["function"])
                c.drawString(current_x, y, func_name)
                current_x += c.stringWidth(func_name, "Courier", font_size)
                
                # Draw the opening parenthesis with default color
                c.setFillColorRGB(*self.code_colors["default"])
                c.drawString(current_x, y, paren)
                current_x += c.stringWidth(paren, "Courier", font_size)
                
                # Remove processed part
                remaining_line = remaining_line[len(func_name) + 1:]
                continue
            
            # If no match found, output the next character with default color
            if not match_found:
                c.setFillColorRGB(*self.code_colors["default"])
                char = remaining_line[0]
                c.drawString(current_x, y, char)
                current_x += c.stringWidth(char, "Courier", font_size)
                remaining_line = remaining_line[1:]

    def _wrap_text(self, text, canvas, font_name, font_size, max_width):
        """Wrap text to fit within max_width"""
        # For multiline code blocks, preserve exact formatting without wrapping
        if font_name == "Courier" and '\n' in text:
            return text.split('\n')
        
        # For simple text (no special formatting needs)
        canvas.setFont(font_name, font_size)
        words = text.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            # Add space between words, but not at the beginning of a line
            if current_line:
                word_with_space = " " + word
                test_width = current_width + canvas.stringWidth(word_with_space, font_name, font_size)
            else:
                word_with_space = word
                test_width = canvas.stringWidth(word_with_space, font_name, font_size)
            
            # Check if this word fits on the current line
            if test_width <= max_width:
                current_line.append(word_with_space)
                current_width = test_width
            else:
                # This word doesn't fit, so start a new line
                if current_line:
                    # Complete the current line
                    lines.append("".join(current_line).strip())
                    # Start a new line with this word
                    current_line = [word]
                    current_width = canvas.stringWidth(word, font_name, font_size)
                else:
                    # The word is too long for the line on its own
                    # We need to break it into pieces character by character
                    remaining = word
                    while remaining:
                        chars_fit = 0
                        for i in range(1, len(remaining) + 1):
                            if canvas.stringWidth(remaining[:i], font_name, font_size) > max_width:
                                chars_fit = i - 1
                                break
                            chars_fit = i
                        
                        # Take at least one character, even if it's too wide
                        chars_fit = max(1, chars_fit)
                        lines.append(remaining[:chars_fit])
                        remaining = remaining[chars_fit:]
        
        # Add the last line if there's anything left
        if current_line:
            lines.append("".join(current_line).strip())
        
        return lines
