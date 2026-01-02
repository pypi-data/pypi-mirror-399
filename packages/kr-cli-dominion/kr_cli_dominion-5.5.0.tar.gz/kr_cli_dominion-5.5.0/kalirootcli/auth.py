"""
Authentication module for KR-CLI v2.0
Handles user registration with email verification, login, and session management.
Uses Supabase Auth via API backend.
"""

import os
import re
import logging
from typing import Optional
from getpass import getpass

from .api_client import api_client
from .distro_detector import detector

logger = logging.getLogger(__name__)


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


class AuthManager:
    """Manages user authentication and sessions via API."""
    
    def __init__(self):
        pass  # Session managed by api_client
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in."""
        return api_client.is_logged_in()
    
    @property
    def current_user(self) -> Optional[dict]:
        """Get current logged-in user info."""
        if not api_client.is_logged_in():
            return None
        return {
            "id": api_client.user_id,
            "email": api_client.email
        }
    
    def logout(self) -> bool:
        """Log out current user."""
        api_client.logout()
        return True
    
    def interactive_register(self) -> Optional[dict]:
        """
        Interactive registration flow with email verification.
        3-step process: Terms → Form → Confirmation
        
        Returns:
            dict with user data if successful, None if failed
        """
        from rich.panel import Panel
        from rich.text import Text
        from rich.align import Align
        from rich import box
        from .ui.display import console, print_error, print_success, print_info, print_warning, clear_screen
        from .ui.colors import STYLE_CYAN, STYLE_BLUE, STYLE_SUCCESS
        
        # ════════════════════════════════════════════════════════════════════
        # PASO 1: TÉRMINOS Y CONDICIONES (PRIMERO - LIMPIAR PANTALLA)
        # ════════════════════════════════════════════════════════════════════
        
        terms_text = """
[bold white]1. NATURALEZA DE LA HERRAMIENTA[/bold white]
   KR-CLI (KaliRoot CLI) es una herramienta profesional avanzada 
   diseñada para operaciones de ciberseguridad ofensiva y defensiva, 
   análisis forense y pruebas de penetración.

[bold white]2. RESPONSABILIDAD DEL USUARIO[/bold white]
   • El uso de esta herramienta es responsabilidad EXCLUSIVA del usuario.
   • Te comprometes a utilizar KR-CLI únicamente en:
     - Entornos controlados de laboratorio
     - Sistemas propios
     - Infraestructuras con autorización explícita por escrito

[bold white]3. EXENCIÓN DE RESPONSABILIDAD[/bold white]
   • Los creadores, desarrolladores y colaboradores de KR-CLI NO se 
     hacen responsables por daños, pérdida de datos, intrusiones no 
     autorizadas o consecuencias legales derivadas del mal uso.

[bold white]4. CUMPLIMIENTO LEGAL[/bold white]
   • Es tu obligación conocer y respetar las leyes locales e 
     internacionales sobre delitos informáticos y ciberseguridad.

[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]

[bold yellow]AL ACEPTAR, CONFIRMAS QUE:[/bold yellow]
   [green]✓[/green] Tienes los conocimientos técnicos necesarios
   [green]✓[/green] Entiendes los riesgos asociados
   [green]✓[/green] Eximes de toda responsabilidad al equipo de KR-CLI
"""
        
        terms_text_raw = """
KR-CLI - TÉRMINOS DE USO Y RESPONSABILIDAD

1. NATURALEZA DE LA HERRAMIENTA
   KR-CLI (KaliRoot CLI) es una herramienta profesional avanzada diseñada para operaciones
   de ciberseguridad ofensiva y defensiva, análisis forense y pruebas de penetración.

2. RESPONSABILIDAD DEL USUARIO
   El uso de esta herramienta es responsabilidad EXCLUSIVA del usuario.
   Te comprometes a utilizar KR-CLI únicamente en entornos controlados,
   sistemas propios o infraestructuras con autorización explícita.

3. EXENCIÓN DE RESPONSABILIDAD
   Los creadores NO se hacen responsables por daños o consecuencias legales.

4. CUMPLIMIENTO LEGAL
   Es tu obligación conocer y respetar las leyes vigentes.
"""
        
        # LIMPIAR PANTALLA Y MOSTRAR TÉRMINOS
        clear_screen()
        
        # Header atractivo
        header = Text()
        header.append("📜  ", style="bold")
        header.append("TÉRMINOS Y CONDICIONES", style="bold rgb(0,255,255)")
        header.append("  📜", style="bold")
        
        console.print()
        console.print(Align.center(Panel(
            header,
            box=box.DOUBLE_EDGE,
            style="rgb(0,100,255)",
            padding=(0, 2)
        )))
        
        console.print("\n[bold yellow]⚠️  LEE ATENTAMENTE ANTES DE CONTINUAR[/bold yellow]\n")
        
        # Panel con los términos
        console.print(Panel(
            terms_text,
            title="[bold rgb(0,255,255)]KR-CLI - Uso Responsable[/bold rgb(0,255,255)]",
            border_style="rgb(0,100,255)",
            box=box.ROUNDED,
            padding=(1, 2)
        ))
        
        console.print()
        console.print("  [bold green]1.[/bold green] [green]✅ ACEPTAR Y CONTINUAR[/green]")
        console.print("  [bold red]0.[/bold red] [red]↩️  VOLVER AL MENÚ[/red]")
        console.print()
        
        while True:
            choice = console.input("  [bold cyan]Selecciona una opción ➜ [/bold cyan]").strip()
            
            if choice == "1":
                console.print()
                print_success("¡Términos aceptados! Continuemos con tu registro...")
                import time
                time.sleep(1)
                break
            elif choice == "0":
                return None
            else:
                console.print("  [red]⚠ Por favor, ingresa 1 o 0[/red]")
        
        # ════════════════════════════════════════════════════════════════════
        # PASO 2: FORMULARIO DE REGISTRO (LIMPIAR PANTALLA)
        # ════════════════════════════════════════════════════════════════════
        
        clear_screen()
        
        # Header del formulario
        form_header = Text()
        form_header.append("📝  ", style="bold")
        form_header.append("CREAR TU CUENTA", style="bold rgb(0,255,255)")
        form_header.append("  📝", style="bold")
        
        console.print()
        console.print(Align.center(Panel(
            form_header,
            box=box.DOUBLE_EDGE,
            style="rgb(0,100,255)",
            padding=(0, 2)
        )))
        
        console.print()
        console.print(Panel(
            "[dim]Completa los siguientes datos para crear tu cuenta.\n"
            "Tu email será usado para verificar tu identidad.[/dim]",
            border_style="dim",
            box=box.ROUNDED
        ))
        console.print()
        
        # Get email
        while True:
            email = console.input("  [rgb(0,255,255)]📧 Correo electrónico:[/rgb(0,255,255)] ").strip().lower()
            
            if not email:
                print_error("El correo electrónico no puede estar vacío")
                continue
            
            if not is_valid_email(email):
                print_error("Formato de correo electrónico inválido")
                continue
            
            break
        
        console.print()
        
        # Get username
        username = console.input("  [rgb(0,255,255)]👤 Nombre de usuario:[/rgb(0,255,255)] ").strip()
        if not username:
            username = email.split("@")[0]
            console.print(f"     [dim](Usando: {username})[/dim]")
        
        console.print()
        
        # Get password
        while True:
            console.print("  [rgb(0,255,255)]🔐 Contraseña:[/rgb(0,255,255)] ", end="")
            password = getpass("")
            
            if len(password) < 6:
                print_error("La contraseña debe tener al menos 6 caracteres")
                continue
            
            console.print("  [rgb(0,255,255)]🔐 Confirmar contraseña:[/rgb(0,255,255)] ", end="")
            password_confirm = getpass("")
            
            if password != password_confirm:
                print_error("Las contraseñas no coinciden. Intenta de nuevo.")
                console.print()
                continue
            
            break
        
        console.print()
        
        # Resumen de datos
        console.print(Panel(
            f"[bold]Resumen de tu cuenta:[/bold]\n\n"
            f"  📧 Email: [rgb(0,255,255)]{email}[/rgb(0,255,255)]\n"
            f"  👤 Usuario: [rgb(0,255,255)]{username}[/rgb(0,255,255)]\n"
            f"  🔐 Contraseña: [dim]••••••••[/dim]",
            title="[bold rgb(0,100,255)]Confirmar datos[/bold rgb(0,100,255)]",
            border_style="rgb(0,100,255)",
            box=box.ROUNDED
        ))
        
        console.print()
        console.print("  [bold green]1.[/bold green] [green]✅ CONTINUAR Y CREAR CUENTA[/green]")
        console.print("  [bold red]0.[/bold red] [red]↩️  CANCELAR[/red]")
        console.print()
        
        while True:
            choice = console.input("  [bold cyan]Selecciona una opción ➜ [/bold cyan]").strip()
            
            if choice == "1":
                break
            elif choice == "0":
                print_warning("Registro cancelado.")
                return None
            else:
                console.print("  [red]⚠ Por favor, ingresa 1 o 0[/red]")
        
        console.print()
        print_info("Creando tu cuenta...")
        
        # Register user via API
        result = api_client.register(email, password, username, terms_accepted=True, terms_text=terms_text_raw)
        
        # ════════════════════════════════════════════════════════════════════
        # PASO 3: MENSAJE DE CONFIRMACIÓN (LIMPIAR PANTALLA)
        # ════════════════════════════════════════════════════════════════════
        
        if result.get("success"):
            import time
            time.sleep(1)
            clear_screen()
            
            # Panel de éxito principal
            success_content = Text()
            success_content.append("\n")
            success_content.append("         ✅ ¡REGISTRO COMPLETADO!\n\n", style="bold green")
            success_content.append("         Hemos enviado un correo de verificación a:\n\n", style="white")
            success_content.append(f"         📧  {email}\n\n", style="bold rgb(0,255,255)")
            success_content.append("         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n", style="dim")
            success_content.append("         Por favor, confirma tu cuenta con el correo\n", style="white")
            success_content.append("         que te acabamos de enviar.\n\n", style="white")
            success_content.append("         Una vez confirmado, podrás acceder con tu\n", style="white")
            success_content.append("         correo y contraseña que acabas de crear.\n\n", style="white")
            success_content.append("         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", style="dim")
            
            console.print()
            console.print(Panel(
                Align.center(success_content),
                title="[bold rgb(0,255,255)]🎉 ¡BIENVENIDO A KR-CLI! 🎉[/bold rgb(0,255,255)]",
                border_style="green",
                box=box.DOUBLE_EDGE,
                padding=(1, 4)
            ))
            
            # Mensaje de agradecimiento
            console.print()
            console.print(Panel(
                "[bold rgb(0,255,255)]¡Gracias por tu apoyo![/bold rgb(0,255,255)]\n\n"
                "[white]KR-CLI es el mejor servicio de IA para ciberseguridad.\n"
                "Estamos emocionados de tenerte en nuestra comunidad.\n\n"
                "Una vez que verifiques tu cuenta, tendrás acceso a:[/white]\n\n"
                "  🔹 Análisis avanzado de comandos\n"
                "  🔹 Asistente IA especializado en seguridad\n"
                "  🔹 Herramientas profesionales de pentesting\n"
                "  🔹 Soporte y actualizaciones continuas\n\n"
                "[bold green]¡Disfruta del mejor servicio de AI con KR-CLI![/bold green]",
                title="[bold rgb(0,100,255)]💎 TU VIAJE COMIENZA AQUÍ 💎[/bold rgb(0,100,255)]",
                border_style="rgb(0,100,255)",
                box=box.ROUNDED,
                padding=(1, 2)
            ))
            
            console.print()
            console.input("[dim]Presiona Enter para volver al menú de inicio de sesión...[/dim]")
            
            return {"email": email, "needs_verification": True}
        else:
            print_error(result.get("error", "Error en el registro"))
            console.input("\n[dim]Presiona Enter para continuar...[/dim]")
            return None
    
    def interactive_login(self) -> Optional[dict]:
        """
        Interactive login flow.
        
        Returns:
            dict with user data if successful, None if failed
        """
        from .ui.display import console, print_error, print_success, print_warning, print_info
        
        console.print("\n[bold rgb(0,255,255)]🔐 INICIAR SESIÓN[/bold rgb(0,255,255)]\n")
        
        # Get email
        email = console.input("[rgb(0,100,255)]📧 Email: [/rgb(0,100,255)]").strip().lower()
        
        if not email:
            print_error("Email es requerido")
            return None
        
        # Get password
        password = getpass("🔐 Password: ")
        
        # Login via API
        print_info("Conectando...")
        result = api_client.login(email, password)
        
        if result.get("success"):
            print_success(f"¡Bienvenido de vuelta!")
            return result.get("data")
        else:
            error = result.get("error", "")
            print_error(error)
            
            # Offer to resend verification if that's the issue
            if "verifi" in error.lower():
                resend = console.input("\n¿Reenviar correo de verificación? [s/N]: ").strip().lower()
                if resend == "s":
                    res = api_client.resend_verification(email)
                    if res.get("success"):
                        print_info("Correo de verificación reenviado. Revisa tu bandeja.")
                    else:
                        print_error("No se pudo reenviar el correo")
            
            return None
    
    def interactive_auth(self) -> Optional[dict]:
        """
        Combined auth flow - shows menu to login or register.
        
        Returns:
            dict with user data if successful, None if user exits
        """
        from .ui.display import console, print_error, print_banner, clear_screen, get_input
        
        while True:
            # Clear screen and show banner per user request
            clear_screen()
            print_banner(show_skull=False)
            
            console.print("  [bold rgb(0,100,255)]1.[/bold rgb(0,100,255)] 🔐 Iniciar sesión")
            console.print("  [bold rgb(0,100,255)]2.[/bold rgb(0,100,255)] 📝 Registrarse (email verificado)")
            console.print("  [bold rgb(0,100,255)]0.[/bold rgb(0,100,255)] ❌ Salir\n")
            
            choice = get_input("Opción")
            
            if choice == "1":
                result = self.interactive_login()
                if result:
                    return result
            elif choice == "2":
                result = self.interactive_register()
                if result and not result.get("needs_verification"):
                    return result
                # If needs verification, loop back to login
            elif choice == "0":
                return None
            else:
                print_error("Opción no válida")


# Global instance
auth_manager = AuthManager()
