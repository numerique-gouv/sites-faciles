class LinkBlock {
  constructor(block, meta) {
    this.block = block;
    this.container = this.block.container[0];
    this.meta = meta;
  }

  initialize() {
    this.select = this.container.querySelector("select");
    if (!this.select) {
      console.warn("Select element not found");
      return;
    }
    const pagechooser = this.container.querySelector(
      '[data-contentpath="page"]'
    );
    const urlInput = this.container.querySelector(
      '[data-contentpath="external_url"]'
    );
    const documentChooser = this.container.querySelector(
      '[data-contentpath="document"]'
    );
    if (pagechooser) pagechooser.style.display = "none";
    if (urlInput) urlInput.style.display = "none";
    if (documentChooser) documentChooser.style.display = "none";

    const updateDisplay = (value) => {
      if (pagechooser)
        pagechooser.style.display = value === "page" ? "block" : "none";
      if (urlInput)
        urlInput.style.display = value === "external_url" ? "block" : "none";
      if (documentChooser)
        documentChooser.style.display = value === "document" ? "block" : "none";
    };
    updateDisplay(this.select.value);

    this.select.addEventListener("change", function () {
      const selectedValue = this.value;
      updateDisplay(selectedValue);
    });
  }
}

class LinkBlockDefinition extends window.wagtailStreamField.blocks
  .StructBlockDefinition {
  render(placeholder, prefix, initialState, initialError) {
    if (this.meta.url_link_text_required) {
      const linkText = this.childBlockDefs.find(
        (obj) => obj.name === "link_text"
      );
      if (linkText) linkText.meta.required = true;
    }

    const block = super.render(placeholder, prefix, initialState, initialError);
    new LinkBlock(block, this.meta).initialize();
    return block;
  }
}

window.telepath.register("blocks.links.LinkBlock", LinkBlockDefinition);
