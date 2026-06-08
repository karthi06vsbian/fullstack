const imagePaths = [
  "home-decor/desk-planter.jpg",
  "home-decor/lamp-shade.jpg",
  "home-decor/wall-tile.jpg",
  "keychains/1761146287570.jpg",
  "keychains/20250225_081702.jpg",
  "keychains/ae79a239-c5ad-46b0-8a09-1406f09278c2.jpg",
  "keychains/alfa-romeo-mc.jpg",
  "keychains/bikelogo.jpg",
  "keychains/image-10.jpg",
  "keychains/img_7185-2.jpg",
  "keychains/instalogo.jpg",
  "keychains/keychain1.jpg",
  "keychains/large_display_1d9b0811-2172-497f-aa51-b40b8a9fed16_762263.jpg",
  "keychains/large_display_bild2_1484735.jpg",
  "keychains/loveheart-full-set.jpg",
  "keychains/narutoshippuden.jpg",
  "keychains/pxl_20240218_001425810.jpg",
  "keychains/snapchat-1104890473.jpg",
  "keychains/sugar-skull-keychains.jpg",
  "pets/15_pig.jpg",
  "pets/20241021_184854.jpg",
  "pets/20241218_105330.jpg",
  "pets/20250103_084439.jpg",
  "pets/20250411_163234.jpg",
  "pets/20250417_191319.jpg",
  "pets/20251009_130515.jpg",
  "pets/chatgpt-image-11-feb-2026-19_54_56.jpg",
  "pets/dsc_3911 2.jpg",
  "pets/dsc_3911.jpg",
  "pets/dsc_3916 2.jpg",
  "pets/dsc_3916.jpg",
  "pets/dsc_3923.jpg",
  "pets/dsc_3928 2.jpg",
  "pets/dsc_3928.jpg",
  "pets/dsc_3935.jpg",
  "pets/dsc_3946.jpg",
  "pets/dsc_3950 2.jpg",
  "pets/dsc_3950.jpg",
  "pets/fox.jpg",
  "pets/giraffe.jpg",
  "pets/img_20240804_105512 2.jpg",
  "pets/img_20240804_105512.jpg",
  "pets/img_20241231_230509 2.jpg",
  "pets/img_20241231_230509.jpg",
  "pets/pic.jpg",
  "pets/pinguin.jpg",
  "pets/playingpets.jpg",
  "projects/architecture-model.jpg",
  "projects/robotics-part.jpg",
  "projects/science-prototype.jpg",
  "toys/20230225_220231.jpg",
  "toys/6cf81c7d4f41d6d9900debb7fd775c04_preview_featured.jpg",
  "toys/anmp0022.jpg",
  "toys/brick1.jpg",
  "toys/coocking_things1.jpg",
  "toys/copie-de-shine-1.jpg",
  "toys/droid-single-copy-1500.jpg",
  "toys/fidget-toy-v2-cut.jpg",
  "toys/imagen-de-whatsapp-2025-09-12-a-las-101959_c28c0827.jpg",
  "toys/img_0738.jpg",
  "toys/img_20210317_151452.jpg",
  "toys/img_3030.jpg",
  "toys/img_4134.jpg",
  "toys/img_6195.jpg",
  "toys/lowpoly_starwars2_preview_featured.jpg",
  "toys/marketing.jpg",
  "toys/photo_2023-08-03_18-33-59.jpg",
  "toys/plus-toy.jpg",
  "toys/portada.jpg",
  "toys/screenshot-2023-06-14-200055-1.jpg",
  "toys/skaermbillede-2024-07-27-232419.jpg",
  "toys/snimok-ekrana-2024-02-01-181902.jpg",
  "useful-appliances/17801800488082.jpg",
  "useful-appliances/20260330_195840.jpg",
  "useful-appliances/20260515_183903.jpg",
  "useful-appliances/20260522_192353.jpg",
  "useful-appliances/20260528_084953469_ios.jpg",
  "useful-appliances/20260528_100731799_ios.jpg",
  "useful-appliances/33cefe9b-8fe2-4b37-a69b-83fd858e65f5.jpg",
  "useful-appliances/chatgpt-image-15-maia-2026-g-17_32_10.jpg",
  "useful-appliances/document.jpg",
  "useful-appliances/dsc00241.jpg",
  "useful-appliances/dsc4625.jpg",
  "useful-appliances/foto_1.jpg",
  "useful-appliances/gemini_generated_image_jptx6ejptx6ejptx.jpg",
  "useful-appliances/gemini_generated_image_yid1mhyid1mhyid1.jpg",
  "useful-appliances/media-23.jpg",
  "useful-appliances/picture2.jpg",
  "useful-appliances/screenshot-2026-06-03-173127.jpg",
  "useful-appliances/shoe1.jpg",
  "useful-appliances/shoerack2.jpg",
  "useful-appliances/v35.jpg",
  "useful-appliances/zrzut-ekranu-2026-06-04-141633.jpg",
];

const categoryLabels = {
  "home-decor": "Home Decor",
  keychains: "Keychains",
  pets: "Pets",
  projects: "Projects",
  toys: "Toys",
  "useful-appliances": "Useful Appliances",
};

const priceRanges = {
  "Home Decor": [349, 1299],
  Keychains: [129, 449],
  Pets: [199, 799],
  Projects: [699, 2499],
  Toys: [199, 999],
  "Useful Appliances": [249, 1199],
};

const materials = ["PLA", "Matte PLA", "Silk PLA", "PETG"];

function hashText(text) {
  let hash = 0;
  for (let index = 0; index < text.length; index += 1) {
    hash = (hash * 31 + text.charCodeAt(index)) >>> 0;
  }
  return hash;
}

function readableName(path) {
  const fileName = path.split("/").pop().replace(/\.[^.]+$/, "");
  const words = fileName.replace(/[_-]/g, " ").split(" ").filter(Boolean);
  const cleaned = words.filter((word) => !["img", "dsc", "pxl"].some((prefix) => word.toLowerCase().startsWith(prefix)));
  return (cleaned.length ? cleaned : words).join(" ").replace(/\b\w/g, (letter) => letter.toUpperCase()).slice(0, 70);
}

function stablePrice(category, path) {
  const [low, high] = priceRanges[category] || [249, 999];
  const stepCount = Math.floor((high - low) / 10);
  return low + ((hashText(path) % stepCount) * 10);
}

const localProducts = [
  {
    id: 1,
    name: "Mini Me Custom Figure",
    category: "Mini Me",
    price: 0,
    rating: 4.9,
    image: "/productsimg/minime.jpg",
    material: "Resin / PLA",
    weight_grams: 350,
    is_featured: true,
    is_custom: true,
    description: "Fully customized 3D miniature from your photo. Quote shared on WhatsApp.",
  },
  ...imagePaths.map((path, index) => {
    const folder = path.split("/")[0];
    const category = categoryLabels[folder] || "Products";
    const hash = hashText(path);
    return {
      id: 1000 + index,
      name: readableName(path),
      category,
      price: stablePrice(category, path),
      rating: 4.5 + ((hash % 5) / 10),
      image: `/productsimg/${path}`,
      material: materials[hash % materials.length],
      weight_grams: 180 + (hash % 620),
      is_featured: index % 9 === 0,
      is_custom: category === "Projects",
      description: `3D printed ${category.toLowerCase()} item ready for order or customization.`,
    };
  }),
];

export default localProducts;
