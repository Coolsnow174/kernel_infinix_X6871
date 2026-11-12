# X6871 kernel prebuilt tree

Prebuilt kernel tree for `device/infinix/X6871` (Infinix GT 20 Pro 5G, MT6895),
extracted from the XOS 16.3.0.155SP20 (`BP2A.250605.031.A3`) dump.

| Path                    | Source                                        |
| ----------------------- | --------------------------------------------- |
| `Image.lz4`             | `boot/kernel` (GKI 6.12, LZ4)                 |
| `dtb/dtb.img`           | `vendor_boot/dtb.img`                         |
| `dtbo.img`              | `dtbo.img`                                    |
| `kernel-headers/`       | dummy headers (satisfies `TARGET_KERNEL_SOURCE`) |
| `modules/ramdisk/`      | `vendor_boot/ramdisk/lib/modules` (242 .ko + load lists) |
| `modules/vendor_dlkm/`  | `vendor_dlkm/lib/modules` (223 .ko + load lists) |
| `modules/system_dlkm/`  | `system_dlkm/lib/modules` (85 .ko + load lists) |
| `modules/odm_dlkm/`     | `odm_dlkm/lib/modules` (75 .ko + load lists)   |
| `firmware/`             | radio partition images (must be filled in)     |

## Missing: radio firmware images

The MTK radio partitions are not part of the dynamic-partition dump. Extract
them from a full OTA payload (or radio dump) and place them in `firmware/`:

`dpm.img gz.img lk.img logo.img mcupm.img md1img.img pi_img.img scp.img
spmfw.img sspm.img tee.img tkv.img`

`BoardConfig.mk` wires them via `BOARD_CUSTOMIMAGES_PARTITION_LIST` /
`BOARD_*_IMAGE_LIST`, and they are flashed as A/B radio partitions.
