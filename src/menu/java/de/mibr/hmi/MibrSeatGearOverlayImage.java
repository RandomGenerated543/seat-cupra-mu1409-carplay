/* SPDX-License-Identifier: MIT
 * Transparent Seat-native gear overlay for the owned MU1409 HOME tile.
 */
package de.mibr.hmi;

import de.vw.mib.widgets.StaticImage;
import de.vw.mib.widgets.models.CommonImageModel;

/** File-backed transparent overlay; the native CarPlay Image[] remains the base. */
public final class MibrSeatGearOverlayImage extends StaticImage implements CommonImageModel {
    public static final String IMAGE_FILE =
            "/mnt/app/eso/hmi/lsd/mibr/icons/mibr_seat_home_gears_rgba_150x150-v2.png";

    public String get_imageFile() { return IMAGE_FILE; }
    public void set_imageFile(String path) { /* immutable package-owned asset */ }
    public int get_imageType() { return CommonImageModel.IMAGE_TYPE_COMMON; }
    public void set_imageType(int type) { }
    public int get_scaleMode() { return CommonImageModel.SCALE_MODE_FIT; }
    public void set_scaleMode(int mode) { }
}
