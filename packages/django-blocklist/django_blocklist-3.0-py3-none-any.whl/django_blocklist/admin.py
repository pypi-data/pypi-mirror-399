from datetime import timezone
import datetime

from django.contrib import admin
from django.http import HttpResponseRedirect

from .models import BlockedIP


@admin.display(description="Reason")
def reason_truncated(entry: BlockedIP) -> str:
    return entry.reason[:20] + ("..." if len(entry.reason) > 20 else "")


@admin.display(description="Cooldown")
def cooldown(entry: BlockedIP) -> str:
    return f"{entry.cooldown} days"


@admin.display(description="Allowed Methods")
def allowed_methods(entry: BlockedIP) -> str:
    if entry.allowed_methods == 0:
        return "NONE"
    else:
        return BlockedIP.method_intflag_to_names(entry.allowed_methods)


@admin.display(description="Days left")
def days_left(entry: BlockedIP) -> str:
    remaining = f"{entry.cooldown - (datetime.datetime.now(timezone.utc) - (entry.last_seen or entry.datetime_added)).days}"
    return remaining


@admin.action(permissions=["view"])
def look_up_first_selected_IP(modeladmin, request, queryset):
    obj = queryset[0]
    return HttpResponseRedirect(f"https://whatismyipaddress.com/ip/{obj.ip}")


class BlockedIPAdmin(admin.ModelAdmin):
    list_display = [
        "ip",
        "datetime_added",
        "last_seen",
        "tally",
        cooldown,
        days_left,
        allowed_methods,
        reason_truncated,
    ]
    list_filter = ["datetime_added", "last_seen", "cooldown", "reason"]
    search_fields = ["ip", "reason"]
    actions = [look_up_first_selected_IP]

    class Meta:
        model = BlockedIP


admin.site.register(BlockedIP, BlockedIPAdmin)
