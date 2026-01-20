const Applet = imports.ui.applet;
const Clutter = imports.gi.Clutter;
const Gio = imports.gi.Gio;
const GLib = imports.gi.GLib;
const Interfaces = imports.misc.interfaces
const Lang = imports.lang;
const St = imports.gi.St;
const Tooltips = imports.ui.tooltips;
const UPowerGlib = imports.gi.UPowerGlib;
const PopupMenu = imports.ui.popupMenu;
const Main = imports.ui.main;
const Settings = imports.ui.settings;
const Util = imports.misc.util;

const BrightnessBusName = "org.cinnamon.SettingsDaemon.Power.Screen";
const KeyboardBusName = "org.cinnamon.SettingsDaemon.Power.Keyboard";
const LegionBusName = "com.legion.Power";

const CSD_BACKLIGHT_NOT_SUPPORTED_CODE = 1;
const PANEL_EDIT_MODE_KEY = "panel-edit-mode";

const {
    DeviceKind: UPDeviceKind,
    DeviceLevel: UPDeviceLevel,
    DeviceState: UPDeviceState,
    Device: UPDevice
} = UPowerGlib

const POWER_PROFILES = {
    "power-saver": _("Power Saver"),
    "balanced": _("Balanced"),
    "performance": _("Performance")
};

const FAN_MODES = {
    "0": _("Quiet"),
    "1": _("Auto"),
    "2": _("Performance")
};

function deviceLevelToString(level) {
    switch (level) {
        case UPDeviceLevel.FULL:
            return _("Battery full");
        case UPDeviceLevel.HIGH:
            return _("Battery almost full");
        case UPDeviceLevel.NORMAL:
            return _("Battery good");
        case UPDeviceLevel.LOW:
            return _("Low battery");
        case UPDeviceLevel.CRITICAL:
            return _("Critically low battery");
        default:
            return _("Unknown");
    }
}

function deviceKindToString(kind) {
    switch (kind) {
        case UPDeviceKind.LINE_POWER:
            return _("AC adapter");
        case UPDeviceKind.BATTERY:
            return _("Laptop battery");
        case UPDeviceKind.UPS:
            return _("UPS");
        case UPDeviceKind.MONITOR:
            return _("Monitor");
        case UPDeviceKind.MOUSE:
            return _("Mouse");
        case UPDeviceKind.KEYBOARD:
            return _("Keyboard");
        case UPDeviceKind.PDA:
            return _("PDA");
        case UPDeviceKind.PHONE:
            return _("Cell phone");
        case UPDeviceKind.MEDIA_PLAYER:
            return _("Media player");
        case UPDeviceKind.TABLET:
            return _("Tablet");
        case UPDeviceKind.COMPUTER:
            return _("Computer");
        case UPDeviceKind.GAMING_INPUT:
            return _("Gaming input");
        case UPDeviceKind.PEN:
            return _("Pen");
        case UPDeviceKind.TOUCHPAD:
            return _("Touchpad");
        case UPDeviceKind.MODEM:
            return _("Modem");
        case UPDeviceKind.NETWORK:
            return _("Network");
        case UPDeviceKind.HEADSET:
            return _("Headset");
        case UPDeviceKind.SPEAKERS:
            return _("Speakers");
        case UPDeviceKind.HEADPHONES:
            return _("Headphones");
        case UPDeviceKind.VIDEO:
            return _("Video");
        case UPDeviceKind.OTHER_AUDIO:
            return _("Audio device");
        case UPDeviceKind.REMOTE_CONTROL:
            return _("Remote control");
        case UPDeviceKind.PRINTER:
            return _("Printer");
        case UPDeviceKind.SCANNER:
            return _("Scanner");
        case UPDeviceKind.CAMERA:
            return _("Camera");
        case UPDeviceKind.WEARABLE:
            return _("Wearable");
        case UPDeviceKind.TOY:
            return _("Toy");
        case UPDeviceKind.BLUETOOTH_GENERIC:
            return _("Bluetooth device");
        default: {
            try {
                return UPDevice.kind_to_string(kind).replaceAll("-", " ").capitalize();
            } catch {
                return _("Unknown");
            }
        }
    }
}

function deviceKindToIcon(kind, icon) {
    switch (kind) {
        case UPDeviceKind.MONITOR:
            return ("video-display");
        case UPDeviceKind.MOUSE:
            return ("input-mouse");
        case UPDeviceKind.KEYBOARD:
            return ("input-keyboard");
        case UPDeviceKind.PHONE:
        case UPDeviceKind.MEDIA_PLAYER:
            return ("phone-apple-iphone");
        case UPDeviceKind.TABLET:
            return ("input-tablet");
        case UPDeviceKind.COMPUTER:
            return ("computer");
        case UPDeviceKind.GAMING_INPUT:
            return ("input-gaming");
        case UPDeviceKind.TOUCHPAD:
            return ("input-touchpad");
        case UPDeviceKind.HEADSET:
            return ("audio-headset");
        case UPDeviceKind.SPEAKERS:
            return ("audio-speakers");
        case UPDeviceKind.HEADPHONES:
            return ("audio-headphones");
        case UPDeviceKind.PRINTER:
            return ("printer");
        case UPDeviceKind.SCANNER:
            return ("scanner");
        case UPDeviceKind.CAMERA:
            return ("camera-photo");
        default:
            if (icon) {
                return icon;
            }
            else {
                return ("battery-full");
            }
    }
}

function reportsPreciseLevels(battery_level) {
    return battery_level == UPDeviceLevel.NONE;
}

class DeviceItem extends PopupMenu.PopupBaseMenuItem {
    constructor(device, status, aliases) {
        super({ reactive: false });

        let [device_id, vendor, model, device_kind, icon, percentage, state, battery_level, time] = device;

        this._box = new St.BoxLayout({ style_class: 'popup-device-menu-item' });
        this._vbox = new St.BoxLayout({ style_class: 'popup-device-menu-item', vertical: true });

        let description = deviceKindToString(device_kind);
        if (vendor != "" || model != "") {
            description = "%s %s".format(vendor, model);
        }

        for (let i = 0; i < aliases.length; ++i) {
            let alias = aliases[i];
            try {
                let parts = alias.split(':=');
                if (parts[0] == device_id) {
                    description = parts[1];
                }
            }
            catch (e) {
                // ignore malformed aliases
                global.logError(alias);
            }
        }

        let statusLabel = null;

        if (battery_level == UPDeviceLevel.NONE) {
            this.label = new St.Label({ text: "%s %d%%".format(description, Math.round(percentage)) });
            statusLabel = new St.Label({ text: "%s".format(status), style_class: 'popup-inactive-menu-item' });
        } else {
            this.label = new St.Label({ text: "%s".format(description) });
            statusLabel = new St.Label({ text: "%s".format(deviceLevelToString(battery_level)), style_class: 'popup-inactive-menu-item' });
        }

        let device_icon = deviceKindToIcon(device_kind, icon);
        if (device_icon == icon) {
            this._icon = new St.Icon({ gicon: Gio.icon_new_for_string(icon), icon_type: St.IconType.SYMBOLIC, style_class: 'popup-menu-icon' });
        }
        else {
            this._icon = new St.Icon({ icon_name: device_icon, icon_type: St.IconType.SYMBOLIC, icon_size: 16 });
        }

        this._box.add_actor(this._icon);
        this._box.add_actor(this.label);

        this._vbox.add_actor(this._box);
        this._vbox.add_actor(statusLabel);

        this.addActor(this._vbox);
    }
}

class BrightnessSlider extends PopupMenu.PopupSliderMenuItem {
    constructor(applet, label, icon, busName, minimum_value) {
        super(0);
        this.actor.hide();

        this._applet = applet;
        this._seeking = false;
        this._minimum_value = minimum_value;
        this._step = .05;

        this.connect("drag-begin", Lang.bind(this, function () {
            this._seeking = true;
        }));
        this.connect("drag-end", Lang.bind(this, function () {
            this._seeking = false;
        }));

        this.icon = new St.Icon({ icon_name: icon, icon_type: St.IconType.SYMBOLIC, icon_size: 16 });
        this.removeActor(this._slider);
        this.addActor(this.icon, { span: 0 });
        this.addActor(this._slider, { span: -1, expand: true });

        this.label = label;
        this.tooltipText = label;
        this.tooltip = new Tooltips.Tooltip(this.actor, this.tooltipText);

        Interfaces.getDBusProxyAsync(busName, Lang.bind(this, function (proxy, error) {
            this._proxy = proxy;
            this._proxy.GetPercentageRemote(Lang.bind(this, this._dbusAcquired));
        }));
    }

    _dbusAcquired(b, error) {
        if (error)
            return;

        try {
            this._proxy.GetStepRemote((step, error) => {
                if (error != null) {
                    if (error.code != CSD_BACKLIGHT_NOT_SUPPORTED_CODE) {
                        global.logError(`Could not get backlight step for ${busName}: ${error.message}`);
                        return;
                    } else {
                        this._step = .05;
                    }
                }
                this._step = (step / 100);
            });
        } catch (e) {
            this._step = .05;
        }

        this._updateBrightnessLabel(b);
        this.setValue(b / 100);
        this.connect("value-changed", Lang.bind(this, this._sliderChanged));

        this.actor.show();

        //get notified
        this._proxy.connectSignal('Changed', Lang.bind(this, this._getBrightness));
        this._applet.menu.connect("open-state-changed", Lang.bind(this, this._getBrightnessForcedUpdate));
    }

    _sliderChanged(slider, value) {
        if (value < this._minimum_value) {
            value = this._minimum_value;
        }

        let i = this._minimum_value;
        let v = value;
        let step = this._step;

        while (i < 1.0) {
            if (v > (i + step)) {
                i = i + step;
                continue;
            }

            if (((i + step) - v) < (v - i)) {
                v = i + step;
            } else {
                v = i;
            }

            break;
        }

        this.setValue(v);

        // A non-zero minimum brightness can cause our stepped value
        // to exceed 100, making the slider jitter (because c-s-d rejects
        // the value)
        this._setBrightness(Math.min(100, Math.round(v * 100)));
    }

    _getBrightness() {
        //This func is called when dbus signal is received.
        //Only update items value when slider is not used
        if (!this._seeking)
            this._getBrightnessForcedUpdate();
    }

    _getBrightnessForcedUpdate() {
        this._proxy.GetPercentageRemote(Lang.bind(this, function (b) {
            this._updateBrightnessLabel(b);
            this.setValue(b / 100);
        }));
    }

    _setBrightness(value) {
        this._proxy.SetPercentageRemote(value, Lang.bind(this, function (b) {
            this._updateBrightnessLabel(b);
        }));
    }

    _updateBrightnessLabel(value) {
        this.tooltipText = this.label;
        if (value)
            this.tooltipText += ": " + value + "%";

        this.tooltip.set_text(this.tooltipText);
        if (this._dragging)
            this.tooltip.show();
    }

    /* Overriding PopupSliderMenuItem so we can modify the scroll step */
    _onScrollEvent(actor, event) {
        let direction = event.get_scroll_direction();

        if (direction == Clutter.ScrollDirection.DOWN) {
            this._proxy.StepDownRemote(function () { });
        }
        else if (direction == Clutter.ScrollDirection.UP) {
            this._proxy.StepUpRemote(function () { });
        }

        this._slider.queue_repaint();
    }
}

class MonitorBrightnessSlider extends PopupMenu.PopupSliderMenuItem {
    constructor(applet, monitorName, displayId) {
        super(0);
        this.actor.hide();

        this._applet = applet;
        this._displayId = displayId;
        this._seeking = false;
        this._step = .05;

        this.connect("drag-begin", Lang.bind(this, function () {
            this._seeking = true;
        }));
        this.connect("drag-end", Lang.bind(this, function () {
            this._seeking = false;
        }));

        this.icon = new St.Icon({ icon_name: "video-display", icon_type: St.IconType.SYMBOLIC, icon_size: 16 });
        this.removeActor(this._slider);
        this.addActor(this.icon, { span: 0 });
        this.addActor(this._slider, { span: -1, expand: true });

        this.label = monitorName;
        this.tooltipText = monitorName;
        this.tooltip = new Tooltips.Tooltip(this.actor, this.tooltipText);

        // Get initial brightness
        this._getBrightness();

        // Connect value change
        this.connect("value-changed", Lang.bind(this, this._sliderChanged));

        this.actor.show();
    }

    _sliderChanged(slider, value) {
        let brightness = Math.round(value * 100);
        brightness = Math.max(0, Math.min(100, brightness));

        // Debounce: wait 300ms before actually setting brightness
        // This prevents flooding ddcutil with commands while dragging
        if (this._setBrightnessTimeout) {
            GLib.source_remove(this._setBrightnessTimeout);
        }
        
        this._setBrightnessTimeout = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 300, Lang.bind(this, function() {
            this._setBrightnessTimeout = 0;
            this._setBrightness(brightness);
            return false;
        }));
        
        // Update label immediately for responsiveness
        this._updateBrightnessLabel(brightness);
    }

    _getBrightness() {
        if (!this._applet._legionProxy) return;
        if (this._gettingBrightness) return; // Prevent overlapping calls
        
        this._gettingBrightness = true;

        try {
            this._applet._legionProxy.GetMonitorBrightnessRemote(this._displayId, Lang.bind(this, function (brightness, error) {
                this._gettingBrightness = false;
                
                if (error) {
                    global.logError("Failed to get monitor brightness: " + error);
                    return;
                }
                this._updateBrightnessLabel(brightness);
                this.setValue(brightness / 100);
            }));
        } catch (e) {
            this._gettingBrightness = false;
            global.logError("Error getting monitor brightness: " + e);
        }
    }

    _getBrightnessForcedUpdate() {
        this._getBrightness();
    }

    _setBrightness(value) {
        if (!this._applet._legionProxy) return;

        try {
            this._applet._legionProxy.SetMonitorBrightnessRemote(this._displayId, value, Lang.bind(this, function (error) {
                if (error) {
                    global.logError("Failed to set monitor brightness: " + error);
                    return;
                }
                this._updateBrightnessLabel(value);
            }));
        } catch (e) {
            global.logError("Error setting monitor brightness: " + e);
        }
    }

    _updateBrightnessLabel(value) {
        this.tooltipText = this.label;
        if (value !== undefined && value !== null)
            this.tooltipText += ": " + value + "%";

        this.tooltip.set_text(this.tooltipText);
        if (this._dragging)
            this.tooltip.show();
    }

    /* Overriding PopupSliderMenuItem so we can modify the scroll step */
    _onScrollEvent(actor, event) {
        let direction = event.get_scroll_direction();
        let currentBrightness = Math.round(this.value * 100);

        if (direction == Clutter.ScrollDirection.DOWN) {
            currentBrightness = Math.max(0, currentBrightness - 5);
        }
        else if (direction == Clutter.ScrollDirection.UP) {
            currentBrightness = Math.min(100, currentBrightness + 5);
        }

        this.setValue(currentBrightness / 100);
        this._setBrightness(currentBrightness);

        this._slider.queue_repaint();
    }
}

class LegionPowerApplet extends Applet.TextIconApplet {
    constructor(metadata, orientation, panel_height, instanceId) {
        super(orientation, panel_height, instanceId);

        this.setAllowedLayout(Applet.AllowedLayout.BOTH);

        this.metadata = metadata;

        this.settings = new Settings.AppletSettings(this, metadata.uuid, instanceId);

        Main.systrayManager.registerTrayIconReplacement("power", metadata.uuid);
        Main.systrayManager.registerTrayIconReplacement("battery", metadata.uuid);

        this.menuManager = new PopupMenu.PopupMenuManager(this);
        this.menu = new Applet.AppletPopupMenu(this, orientation);
        this.menuManager.addMenu(this.menu);

        this.aliases = global.settings.get_strv("device-aliases");

        this._deviceItems = [];
        this._devices = [];
        this._primaryDeviceId = null;
        this.panel_icon_name = ''; // remember the panel icon name (so we only set it when it actually changes)

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        // Store brightness/keyboard sliders for later (will be added after monitors)
        this.brightness = new BrightnessSlider(this, _("Brightness"), "display-brightness", BrightnessBusName, 0);
        this.keyboard = new BrightnessSlider(this, _("Keyboard backlight"), "keyboard-brightness", KeyboardBusName, 0);
        
        // Don't add brightness slider yet - will be added as part of External Monitors
        // Only add keyboard backlight here
        this.menu.addMenuItem(this.keyboard);

        try {
            // Hadess interface
            let PowerProfilesInterface = `<node>
              <interface name="net.hadess.PowerProfiles">
                <property name="ActiveProfile" type="s" access="readwrite" />
                <property name="PerformanceDegraded" type="s" access="read" />
                <property name="Profiles" type="aa{sv}" access="read" />
                <property name="ActiveProfileHolds" type="aa{sv}" access="read" />
              </interface>
            </node>`;
            let PowerProfilesProxy = Gio.DBusProxy.makeProxyWrapper(PowerProfilesInterface);
            this._profilesProxy = new PowerProfilesProxy(Gio.DBus.system, "net.hadess.PowerProfiles", "/net/hadess/PowerProfiles");
            // Upower if hadess doesn't work..
            if (!this._profilesProxy.Profiles) {
                // UPower interface
                let PowerProfilesInterface = `<node>
                  <interface name="org.freedesktop.UPower.PowerProfiles">
                    <property name="ActiveProfile" type="s" access="readwrite" />
                    <property name="PerformanceDegraded" type="s" access="read" />
                    <property name="Profiles" type="aa{sv}" access="read" />
                    <property name="ActiveProfileHolds" type="aa{sv}" access="read" />
                  </interface>
                </node>`;
                let PowerProfilesProxy = Gio.DBusProxy.makeProxyWrapper(PowerProfilesInterface);
                this._profilesProxy = new PowerProfilesProxy(Gio.DBus.system, "org.freedesktop.UPower.PowerProfiles", "/org/freedesktop/UPower/PowerProfiles");
            }
        } catch {
           this._profilesProxy = null;
        }
        
        if (this._profilesProxy && this._profilesProxy.Profiles) {
            this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
            this.contentSection = new PopupMenu.PopupMenuSection();

            this.ActiveProfile = this._profilesProxy.ActiveProfile;
            this.Profiles = this._profilesProxy.Profiles;

            this._proxyId = this._profilesProxy.connect("g-properties-changed", (proxy, changed, invalidated) => {
                for (let [changedProperty, changedValue] of Object.entries(changed.deepUnpack())) {
                    if (["ActiveProfile", "Profiles"].includes(changedProperty))
                        this[changedProperty] = changedValue.deepUnpack();
                    this._updateProfile();
                }
            });

            this._updateProfile();
        }

        // Legion-specific controls
        this._legionProxy = null;
        this._conservationSwitch = null;
        this._rapidChargeSwitch = null;
        this._fanModeSection = null;
        
        // External monitor controls
        this._externalMonitors = [];
        this._monitorSliders = [];
        this._monitorRefreshId = 0;
        
        this.settings.bind("show-legion-features", "show_legion_features", this._setupLegionControls);
        this.settings.bind("show-external-monitors", "show_external_monitors", this._setupExternalMonitors);
        this._setupLegionControls();

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        this.menu.addSettingsAction(_("Power Settings"), 'power');

        this.actor.connect("scroll-event", Lang.bind(this, this._onScrollEvent));

        this._proxy = null;

        global.settings.connect('changed::' + PANEL_EDIT_MODE_KEY, Lang.bind(this, this._onPanelEditModeChanged));

        this.csd_power_watch_id = Gio.bus_watch_name(Gio.BusType.SESSION, "org.cinnamon.SettingsDaemon.Power", 0, (c, name) => {
            Interfaces.getDBusProxyAsync("org.cinnamon.SettingsDaemon.Power", Lang.bind(this, function (proxy, error) {
                Gio.bus_unwatch_name(this.csd_power_watch_id);
                this.csd_power_watch_id = 0;

                if (error) {
                    global.logError("Could not connect to csd-power", error.message);
                    return;
                }

                this._proxy = proxy;

                this._proxy.connect("g-properties-changed", Lang.bind(this, this._devicesChanged));
                global.settings.connect('changed::device-aliases', Lang.bind(this, this._on_device_aliases_changed));
                this.settings.bind("labelinfo", "labelinfo", this._devicesChanged);
                this.settings.bind("showmulti", "showmulti", this._devicesChanged);

                this._devicesChanged();
            }));
        }, null);

        this.set_show_label_in_vertical_panels(false);
    }

    _setupLegionControls() {
        if (!this.show_legion_features) {
            if (this._legionSection) {
                this._legionSection.destroy();
                this._legionSection = null;
            }
            return;
        }

        // Try to connect to Legion D-Bus service
        try {
            let LegionInterface = `<node>
              <interface name="com.legion.Power.Manager">
                <method name="GetConservationMode">
                  <arg type="b" direction="out" name="enabled" />
                </method>
                <method name="SetConservationMode">
                  <arg type="b" direction="in" name="enable" />
                </method>
                <method name="GetRapidCharge">
                  <arg type="b" direction="out" name="enabled" />
                </method>
                <method name="SetRapidCharge">
                  <arg type="b" direction="in" name="enable" />
                </method>
                <method name="GetFanMode">
                  <arg type="s" direction="out" name="mode" />
                </method>
                <method name="SetFanMode">
                  <arg type="s" direction="in" name="mode" />
                </method>
                <method name="GetExternalMonitors">
                  <arg type="aa{sv}" direction="out" name="monitors" />
                </method>
                <method name="GetMonitorBrightness">
                  <arg type="i" direction="in" name="display_id" />
                  <arg type="i" direction="out" name="brightness" />
                </method>
                <method name="SetMonitorBrightness">
                  <arg type="i" direction="in" name="display_id" />
                  <arg type="i" direction="in" name="brightness" />
                </method>
                <method name="RefreshExternalMonitors">
                </method>
                <signal name="MonitorBrightnessChanged">
                  <arg name="display_id" type="i" />
                  <arg name="brightness" type="i" />
                </signal>
              </interface>
            </node>`;
            let LegionProxy = Gio.DBusProxy.makeProxyWrapper(LegionInterface);
            this._legionProxy = new LegionProxy(Gio.DBus.system, LegionBusName, "/com/legion/Power");

            // Create Legion controls section
            this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
            
            this._legionSection = new PopupMenu.PopupMenuSection();
            
            // Header
            let headerItem = new PopupMenu.PopupMenuItem(_("Legion Controls"), { reactive: false, style_class: 'legion-section-header' });
            this._legionSection.addMenuItem(headerItem);

            // Conservation Mode toggle with explanation
            this._conservationSwitch = new PopupMenu.PopupSwitchMenuItem(_("Conservation Mode (limits charge to ~60%)"));
            this._conservationSwitch.connect('toggled', Lang.bind(this, this._onConservationToggled));
            this._legionSection.addMenuItem(this._conservationSwitch);

            // Rapid Charge toggle
            this._rapidChargeSwitch = new PopupMenu.PopupSwitchMenuItem(_("Rapid Charge"));
            this._rapidChargeSwitch.connect('toggled', Lang.bind(this, this._onRapidChargeToggled));
            this._legionSection.addMenuItem(this._rapidChargeSwitch);

            // Fan Mode selector
            this._fanModeSection = new PopupMenu.PopupMenuSection();
            let fanHeader = new PopupMenu.PopupMenuItem(_("Fan Mode"), { reactive: false });
            this._fanModeSection.addMenuItem(fanHeader);

            for (let mode in FAN_MODES) {
                let item = new PopupMenu.PopupMenuItem(FAN_MODES[mode]);
                item._fanMode = parseInt(mode);
                item.connect('activate', Lang.bind(this, function() {
                    this._setFanMode(item._fanMode);
                }));
                this._fanModeSection.addMenuItem(item);
            }
            this._legionSection.addMenuItem(this._fanModeSection);

            // Open Power Manager button
            let openManagerItem = new PopupMenu.PopupMenuItem(_("Open Legion Power Manager"));
            openManagerItem.connect('activate', function() {
                Util.spawnCommandLine("legion-power-gui");
            });
            this._legionSection.addMenuItem(openManagerItem);

            // Listen for property changes
            this._legionProxy.connect("g-properties-changed", Lang.bind(this, this._updateLegionControls));
            
            // Initial update
            this._updateLegionControls();
            
            // Setup external monitors FIRST (async, before Legion Controls)
            GLib.timeout_add(GLib.PRIORITY_LOW, 100, Lang.bind(this, function() {
                this._setupExternalMonitors();
                
                // THEN add Legion Controls section (after monitors are set up)
                GLib.timeout_add(GLib.PRIORITY_LOW, 50, Lang.bind(this, function() {
                    if (this._legionSection) {
                        this.menu.addMenuItem(this._legionSection);
                    }
                    return false;
                }));
                
                return false; // Don't repeat
            }));

        } catch (e) {
            global.logError("Legion Power: Could not connect to Legion D-Bus service: " + e);
            this._legionProxy = null;
        }
    }

    _setupExternalMonitors() {
        global.log("Legion Power: _setupExternalMonitors called");
        
        // Clean up existing monitors
        if (this._monitorSection) {
            this._monitorSection.destroy();
            this._monitorSection = null;
        }
        
        for (let slider of this._monitorSliders) {
            slider.destroy();
        }
        this._monitorSliders = [];
        
        if (this._monitorRefreshId) {
            GLib.source_remove(this._monitorRefreshId);
            this._monitorRefreshId = 0;
        }

        if (!this.show_external_monitors) {
            global.log("Legion Power: External monitors disabled in settings");
            return;
        }

        // Try to get monitors from Legion D-Bus service
        if (!this._legionProxy) {
            global.log("Legion Power: No Legion D-Bus proxy available");
            return;
        }
        
        global.log("Legion Power: Refreshing monitor cache...");

        // Refresh monitor cache first to detect newly connected monitors
        try {
            this._legionProxy.RefreshExternalMonitorsRemote(Lang.bind(this, function(error) {
                if (error) {
                    global.logWarning("Could not refresh monitor cache: " + error);
                }
                
                global.log("Legion Power: Cache refreshed, getting monitors...");
                
                // Now get the fresh monitor list
                try {
                    this._legionProxy.GetExternalMonitorsRemote(Lang.bind(this, function (monitors, error) {
                if (error) {
                    global.logWarning("Failed to get external monitors: " + error);
                    return;
                }

                // D-Bus returns array in array, unwrap it
                if (monitors && monitors.length === 1 && Array.isArray(monitors[0])) {
                    global.log("Legion Power: Unwrapping nested array");
                    monitors = monitors[0];
                }
                
                global.log("Legion Power: Got " + (monitors ? monitors.length : 0) + " monitor(s) from D-Bus");

                if (!monitors || monitors.length === 0) {
                    global.logWarning("No external DDC/CI monitors detected");
                    return;
                }

                // Create monitors section
                this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
                
                this._monitorSection = new PopupMenu.PopupMenuSection();
                
                // Header
                let headerItem = new PopupMenu.PopupMenuItem(_("Displays"), { reactive: false });
                this._monitorSection.addMenuItem(headerItem);

                // Add built-in laptop display first (if available)
                if (this.brightness && this.brightness.actor.visible) {
                    this._monitorSection.addMenuItem(this.brightness);
                }

                // Add slider for each external monitor
                for (let i = 0; i < monitors.length; i++) {
                    let mon = monitors[i];
                    
                    // D-Bus returns variants - need to unpack
                    let monName = "Unknown Monitor";
                    let monId = 1;
                    
                    try {
                        // Try to extract from dictionary
                        if (mon['name'] && typeof mon['name'].unpack === 'function') {
                            monName = mon['name'].unpack();
                        } else if (typeof mon['name'] === 'string') {
                            monName = mon['name'];
                        }
                        
                        if (mon['id'] && typeof mon['id'].unpack === 'function') {
                            monId = mon['id'].unpack();
                        } else if (typeof mon['id'] === 'number') {
                            monId = mon['id'];
                        }
                    } catch (e) {
                        global.logError("Legion Power: Failed to unpack monitor data: " + e);
                    }
                    
                    global.log("Legion Power: Creating slider for " + monName + " (id=" + monId + ")");
                    
                    let slider = new MonitorBrightnessSlider(
                        this,
                        monName,
                        monId
                    );
                    this._monitorSection.addMenuItem(slider);
                    this._monitorSliders.push(slider);
                }

                // Add refresh button with icon
                let refreshItem = new PopupMenu.PopupIconMenuItem(_("Refresh Displays"), "view-refresh-symbolic", St.IconType.SYMBOLIC);
                refreshItem.connect('activate', Lang.bind(this, function() {
                    global.log("Legion Power: Manual refresh requested");
                    this._setupExternalMonitors();
                }));
                this._monitorSection.addMenuItem(refreshItem);

                this.menu.addMenuItem(this._monitorSection);

                global.log("External monitors initialized: " + monitors.length);

                // Auto-refresh brightness values every 60 seconds
                this._monitorRefreshId = GLib.timeout_add_seconds(
                    GLib.PRIORITY_DEFAULT,
                    60,
                    Lang.bind(this, this._refreshExternalMonitors)
                );
                    }));
                } catch (e) {
                    global.logError("Error getting external monitors: " + e);
                }
            }));
        } catch (e) {
            global.logError("Error refreshing monitor cache: " + e);
        }
    }

    _refreshExternalMonitors() {
        // Refresh brightness values for all monitors
        for (let slider of this._monitorSliders) {
            slider._getBrightnessForcedUpdate();
        }
        
        return true; // Keep the timer running
    }

    _updateLegionControls() {
        if (!this._legionProxy || !this._conservationSwitch || !this._rapidChargeSwitch)
            return;

        try {
            // Use D-Bus methods instead of properties
            this._legionProxy.GetConservationModeRemote(Lang.bind(this, function(conservation, error) {
                if (!error) {
                    this._conservationSwitch.setToggleState(conservation);
                }
            }));
            
            this._legionProxy.GetRapidChargeRemote(Lang.bind(this, function(rapidCharge, error) {
                if (!error) {
                    this._rapidChargeSwitch.setToggleState(rapidCharge);
                }
            }));
            
            this._legionProxy.GetFanModeRemote(Lang.bind(this, function(fanMode, error) {
                if (!error && this._fanModeSection) {
                    let items = this._fanModeSection._getMenuItems();
                    for (let i = 0; i < items.length; i++) {
                        if (items[i]._fanMode !== undefined) {
                            items[i].setShowDot(items[i]._fanMode === fanMode);
                        }
                    }
                }
            }));
        } catch (e) {
            global.logError("Legion Power: Error updating controls: " + e);
        }
    }

    _onConservationToggled(item, state) {
        if (!this._legionProxy)
            return;

        try {
            // Use D-Bus method instead of property
            this._legionProxy.SetConservationModeRemote(state, Lang.bind(this, function(error) {
                if (error) {
                    global.logError("Legion Power: Error setting conservation mode: " + error);
                }
            }));
        } catch (e) {
            global.logError("Legion Power: Error setting conservation mode: " + e);
        }
    }

    _onRapidChargeToggled(item, state) {
        if (!this._legionProxy)
            return;

        try {
            // Use D-Bus method instead of property
            this._legionProxy.SetRapidChargeRemote(state, Lang.bind(this, function(error) {
                if (error) {
                    global.logError("Legion Power: Error setting rapid charge: " + error);
                }
            }));
        } catch (e) {
            global.logError("Legion Power: Error setting rapid charge: " + e);
        }
    }

    _setFanMode(mode) {
        if (!this._legionProxy)
            return;

        try {
            // Use D-Bus method instead of property
            this._legionProxy.SetFanModeRemote(mode, Lang.bind(this, function(error) {
                if (error) {
                    global.logError("Legion Power: Error setting fan mode: " + error);
                }
            }));
        } catch (e) {
            global.logError("Legion Power: Error setting fan mode: " + e);
        }
    }

    _onPanelEditModeChanged() {
        if (global.settings.get_boolean(PANEL_EDIT_MODE_KEY)) {
            if (!this.actor.visible) {
                this.set_applet_icon_symbolic_name("battery-missing");
                this.set_applet_enabled(true);
            }
        }
        else {
            this._devicesChanged();
        }
    }

    _on_device_aliases_changed() {
        this.aliases = global.settings.get_strv("device-aliases");
        this._devicesChanged();
    }

    _onButtonPressEvent(actor, event) {
        //toggle keyboard brightness on middle click
        if (event.get_button() === 2) {
            if (this.keyboard._proxy)
                this.keyboard._proxy.ToggleRemote(function () { });
        }
        return Applet.Applet.prototype._onButtonPressEvent.call(this, actor, event);
    }

    on_applet_clicked(event) {
        this.menu.toggle();
    }

    _onScrollEvent(actor, event) {
        //adjust screen brightness on scroll
        let direction = event.get_scroll_direction();
        if (direction == Clutter.ScrollDirection.UP) {
            if (this.brightness._proxy)
                this.brightness._proxy.StepUpRemote(function () { });
        } else if (direction == Clutter.ScrollDirection.DOWN) {
            if (this.brightness._proxy)
                this.brightness._proxy.StepDownRemote(function () { });
        }
        if (this.brightness._proxy)
            this.brightness._getBrightnessForcedUpdate();
    }

    _getDeviceStatus(device) {
        let status = "";
        let [device_id, vendor, model, device_kind, icon, percentage, state, battery_level, seconds] = device;

        let time = Math.round(seconds / 60);
        let minutes = time % 60;
        let hours = Math.floor(time / 60);

        if (state == UPDeviceState.UNKNOWN) {
            status = "";
        }
        else if (state == UPDeviceState.CHARGING) {
            if (time == 0) {
                status = _("Charging");
            }
            else if (time >= 60) {
                if (minutes == 0) {
                    status = ngettext("Charging - %d hour until fully charged", "Charging - %d hours until fully charged", hours).format(hours);
                }
                else {
                    /* Translators: this is a time string, as in "%d hours %d minutes remaining" */
                    let template = _("Charging - %d %s %d %s until fully charged");
                    status = template.format(hours, ngettext("hour", "hours", hours), minutes, ngettext("minute", "minutes", minutes));
                }
            }
            else {
                status = ngettext("Charging - %d minute until fully charged", "Charging - %d minutes until fully charged", minutes).format(minutes);
            }
        }
        else if (state == UPDeviceState.FULLY_CHARGED) {
            status = _("Fully charged");
        }
        else if (state == UPDeviceState.DISCHARGING) {
            if (time == 0) {
                status = _("Using battery power");
            }
            else if (time >= 60) {
                if (minutes == 0) {
                    status = ngettext("Using battery power - %d hour remaining", "Using battery power - %d hours remaining", hours).format(hours);
                }
                else {
                    /* Translators: this is a time string, as in "%d hours %d minutes remaining" */
                    let template = _("Using battery power - %d %s %d %s remaining");
                    status = template.format(hours, ngettext("hour", "hours", hours), minutes, ngettext("minute", "minutes", minutes));
                }
            }
            else {
                status = ngettext("Using battery power - %d minute remaining", "Using battery power - %d minutes remaining", minutes).format(minutes);
            }
        }
        else if (state == UPDeviceState.EMPTY) {
            status = _("Fully discharged");
        }
        else {
            status = _("Not charging");
        }

        return status;
    }

    on_panel_height_changed() {
        if (this._proxy)
            this._devicesChanged();
    }

    showDeviceInPanel(device) {
        let [device_id, vendor, model, device_kind, icon, percentage, state, battery_level, seconds] = device;
        let status = this._getDeviceStatus(device);
        this.set_applet_tooltip(status);
        let labelText = "";
        if (this.labelinfo == "nothing") {
            ;
        }
        else if (this.labelinfo == "time" && seconds != 0) {
            let time = Math.round(seconds / 60);
            let minutes = time % 60;
            let hours = Math.floor(time / 60);
            labelText = C_("time of battery remaining", "%d:%02d").format(hours, minutes);
        }
        else if (this.labelinfo == "percentage" || (this.labelinfo == "percentage_time" && seconds == 0)) {
            labelText = C_("percent of battery remaining", "%d%%").format(Math.round(percentage));
        }
        else if (this.labelinfo == "percentage_time") {
            let time = Math.round(seconds / 60);
            let minutes = Math.floor(time % 60);
            let hours = Math.floor(time / 60);
            labelText = C_("percent of battery remaining", "%d%%").format(Math.round(percentage)) + " (" +
                C_("time of battery remaining", "%d:%02d").format(hours, minutes) + ")";
        }
        this.set_applet_label(labelText);

        if (icon) {
            if (this.panel_icon_name != icon) {
                this.panel_icon_name = icon;
                this.set_applet_icon_symbolic_name('battery-full');
                let gicon = Gio.icon_new_for_string(icon);
                this._applet_icon.gicon = gicon;
            }
        }
        else {
            if (this.panel_icon_name != 'battery-full') {
                this.panel_icon_name = 'battery-full';
                this.set_applet_icon_symbolic_name('battery-full');
            }
        }

        this._applet_icon.set_style_class_name('system-status-icon');
    }

    _updateProfile() {
        this.contentSection.removeAll();

        for (let profileNum = 0; profileNum < this.Profiles.length; profileNum++) {
            let profileName = this.Profiles[profileNum].Profile.unpack();
            let item;
            if (profileName == this.ActiveProfile) {
                this.profileIndex = profileNum;
                item = new PopupMenu.PopupMenuItem(POWER_PROFILES[profileName], { style_class: 'popup-device-menu-item', reactive: false });
                item.setShowDot(true);
            } else {
                item = new PopupMenu.PopupMenuItem(POWER_PROFILES[profileName]);
                item.connect("activate", Lang.bind(this, function () {
                    this._changeProfile(profileName);
                    this.menu.toggle();
                }));
            }
            this.contentSection.addMenuItem(item);
        }

        this.menu.addMenuItem(this.contentSection);
    }

    _changeProfile(newProfile) {
        this._profilesProxy.ActiveProfile = newProfile;
        this.ActiveProfile = this._profilesProxy.ActiveProfile;
    }

    _devicesChanged() {

        this._devices = [];
        this._primaryDevice = null;
        this._primaryDeviceId = null;

        if (!this._proxy)
            return;

        // Identify the primary battery device
        this._proxy.GetPrimaryDeviceRemote(Lang.bind(this, function (device, error) {
            if (error) {
                this._primaryDeviceId = null;
            }
            else {
                if (device.length == 1) {
                    // Primary Device can be an array of primary devices rather than a single device, in that case, take the first one.
                    device = device[0];
                }
                let [device_id, vendor, model, device_kind, icon, percentage, state, battery_level, seconds] = device
                this._primaryDeviceId = device_id;
            }

            // Scan battery devices
            this._proxy.GetDevicesRemote(Lang.bind(this, function (result, error) {
                this._deviceItems.forEach(function (i) { i.destroy(); });
                this._deviceItems = [];
                let devices_stats = [];
                let pct_support_count = 0;
                let _devices = []; let _deviceItems = [];

                if (!error) {
                    let devices = result[0];
                    let position = 0;
                    for (let i = 0; i < devices.length; i++) {
                        let [device_id, vendor, model, device_kind, icon, percentage, state, battery_level, seconds] = devices[i];

                        // Ignore LINE_POWER devices
                        if (device_kind == UPDeviceKind.LINE_POWER)
                            continue;

                        // Ignore devices which state is unknown
                        if (state == UPDeviceState.UNKNOWN)
                            continue;

                        if (reportsPreciseLevels(battery_level)) {
                            // Devices that give accurate % charge will return this for battery level.
                            pct_support_count++;
                        }

                        let stats = "%s (%d%%)".format(deviceKindToString(device_kind), percentage);
                        devices_stats.push(stats);
                        _devices.push(devices[i]);

                        if (this._primaryDeviceId == null || this._primaryDeviceId == device_id) {
                            // Info for the primary battery (either the primary device, or any battery device if there is no primary device)
                            if (device_kind == UPDeviceKind.BATTERY && this._primaryDevice == null) {
                                this._primaryDevice = devices[i];
                            }
                        }

                        let status = this._getDeviceStatus(devices[i]);
                        let item = new DeviceItem(devices[i], status, this.aliases);
                        this.menu.addMenuItem(item, position);
                        _deviceItems.push(item);
                        position++;
                    }
                }
                else {
                    global.logError(error);
                }


                this._devices = _devices;
                this._deviceItems = _deviceItems;

                // The menu is built. Below, we update the information present in the panel (icon, tooltip and label)
                this.set_applet_enabled(true);
                let panel_device = null;

                // Things should only ever be in the panel if they provide accurate reporting (percentages), otherwise
                // they're probably not likely to drain quickly enough to merit showing except on demand, in the popup menu.

                // One or more devices, one is a real battery, and multi-device is disabled
                if (this._primaryDevice != null && (!this.showmulti || (this._devices.length === 1) && pct_support_count === 1)) {
                    this.showDeviceInPanel(this._primaryDevice);
                }
                else {
                    // One device, not marked primary, but has accurate reporting (not sure this will ever happen).
                    if (this._devices.length === 1 && pct_support_count === 1) {
                        this.showDeviceInPanel(this._devices[0]);
                    }
                    else if (this._devices.length > 0) {
                        // Show a summary
                        let labelText = "";
                        if (this.labelinfo !== "nothing") {
                            let num = 0;

                            for (let i = 0; i < this._devices.length; i++) {
                                let [, , , , , percentage, , battery_level, seconds] = this._devices[i];

                                // Skip devices without accurate reporting
                                if (!reportsPreciseLevels(battery_level)) {
                                    continue;
                                }

                                // Only number them if we'll have multiple items
                                if (pct_support_count > 1) {
                                    labelText += (num++) + ': ';
                                }

                                if (this.labelinfo == "time" && seconds !== 0) {
                                    let time = Math.round(seconds / 60);
                                    let minutes = time % 60;
                                    let hours = Math.floor(time / 60);
                                    labelText += C_("time of battery remaining", "%d:%02d").format(hours, minutes);
                                }
                                else if (this.labelinfo == "percentage" || (this.labelinfo == "percentage_time" && seconds === 0)) {
                                    labelText += C_("percent of battery remaining", "%d%%").format(Math.round(percentage));
                                }
                                else if (this.labelinfo == "percentage_time") {
                                    let time = Math.round(seconds / 60);
                                    let minutes = Math.floor(time % 60);
                                    let hours = Math.floor(time / 60);
                                    labelText += C_("percent of battery remaining", "%d%%").format(Math.round(percentage)) + " (" +
                                        C_("time of battery remaining", "%d:%02d").format(hours, minutes) + ")";
                                }

                                // Only add a gap if we have remaining valid devices to show.
                                if (num < pct_support_count) {
                                    labelText += '  ';
                                }
                            }
                        }

                        this.set_applet_tooltip(devices_stats.join(", "));
                        this.set_applet_label(labelText);
                        let icon = this._proxy.Icon;
                        if (icon) {
                            if (icon != this.panel_icon_name) {
                                this.panel_icon_name = icon;
                                this.set_applet_icon_symbolic_name('battery-full');
                                let gicon = Gio.icon_new_for_string(icon);
                                this._applet_icon.gicon = gicon;
                            }
                        }
                        else {
                            if (this.panel_icon_name != 'battery-full') {
                                this.panel_icon_name = 'battery-full';
                                this.set_applet_icon_symbolic_name('battery-full');
                            }
                        }
                    }
                    else {
                        // If there are no battery devices, show brightness info or disable the applet
                        this.set_applet_label("");
                        if (this.brightness.actor.visible) {
                            // Show the brightness info
                            this.set_applet_tooltip(_("Brightness"));
                            this.panel_icon_name = 'display-brightness';
                            this.set_applet_icon_symbolic_name('display-brightness');
                        }
                        else if (this.keyboard.actor.visible) {
                            // Show the brightness info
                            this.set_applet_tooltip(_("Keyboard backlight"));
                            this.panel_icon_name = 'keyboard-brightness';
                            this.set_applet_icon_symbolic_name('keyboard-brightness');
                        }
                        else {
                            // Disable the applet
                            this.set_applet_enabled(false);
                        }
                    }
                }
            }));
        }));
    }

    on_applet_removed_from_panel() {
        Main.systrayManager.unregisterTrayIconReplacement(this.metadata.uuid);

        if (this._profilesProxy && this._proxyId)
            this._profilesProxy.disconnect(this._proxyId);

        if (this.csd_power_watch_id)
            Gio.bus_unwatch_name(this.csd_power_watch_id);
        
        // Cleanup external monitors
        if (this._monitorRefreshId) {
            GLib.source_remove(this._monitorRefreshId);
            this._monitorRefreshId = 0;
        }
    }
}

function main(metadata, orientation, panel_height, instanceId) {
    return new LegionPowerApplet(metadata, orientation, panel_height, instanceId);
}
