import base64
from pathlib import Path
import geopandas as gpd
import folium


def _find_image(images_dir: Path, name: str):
    """
    Try to find an image matching POI name.
    """

    for ext in [".jpg", ".jpeg", ".png"]:
        p = images_dir / f"{name}{ext}"
        if p.exists():
            return p
    return None


def _build_popup_html(name: str, img_path: Path | None, link: str):
    """
    Create HTML for POI popup.
    """

    display_name = str(name).replace("_", " ")

    html = f"""
    <div style="font-family: Arial; width:280px">
        <h4 style="margin:0 0 8px 0">{display_name}</h4>
    """

    if img_path:
        encoded = base64.b64encode(img_path.read_bytes()).decode("utf-8")

        html += f"""
        <img src="data:image/jpeg;base64,{encoded}"
             style="width:280px;
                    height:auto;
                    border-radius:8px;
                    margin-bottom:10px;">
        """
    else:
        html += "<i>No image available</i>"

    if link:
        html += f"""
        <div style="margin-top:8px;">
            <a href="{link}" target="_blank"
               style="text-decoration:none;
                      font-weight:bold;
                      color:#1a73e8;">
                🔗 Plus d'informations
            </a>
        </div>
        """

    html += "</div>"
    return html


def build_poi_layer(poi_file: Path, images_dir: Path):
    """
    Load POIs and return a Folium FeatureGroup layer.
    """

    gdf = gpd.read_file(poi_file)

    layer = folium.FeatureGroup(
        name="Points of Interest",
        show=True,
    )

    for _, row in gdf.iterrows():

        geom = row.geometry
        if geom is None:
            continue

        # Handle geometry types
        if geom.geom_type == "Point":
            lon, lat = geom.x, geom.y

        elif geom.geom_type == "MultiPoint":
            pt = list(geom.geoms)[0]
            lon, lat = pt.x, pt.y

        else:
            continue

        name = row.get("name")
        if not name:
            continue

        link = row.get("link", "")

        img_path = _find_image(images_dir, name)

        popup_html = _build_popup_html(name, img_path, link)

        popup = folium.Popup(popup_html, max_width=320)

        folium.Marker(
            location=[lat, lon],
            popup=popup,
            tooltip=str(name).replace("_", " "),
            icon=folium.Icon(color="cadetblue", icon="info-sign"),
        ).add_to(layer)

    return layer
