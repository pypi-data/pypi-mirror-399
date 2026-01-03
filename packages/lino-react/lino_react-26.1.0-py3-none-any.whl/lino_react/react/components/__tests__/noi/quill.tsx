import React from "react";
import * as t from "../../types";
import i18n from "../../i18n";
import { Delta, Quill, getQuillModules, textboxId } from "../../quillmodules";

// Mock ResizeObserver which is not available in jsdom
global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
};

describe("Quill Editor Module", () => {
    const valueRef = { current: "" };
    let modules: t.ObjectAny, quill: Quill, quillContainer: HTMLDivElement;
    
    beforeAll(() => {
        // Set up window.App mock
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (window as any).App = {
            state: {
                site_data: {
                    suggestors: ["@", "#"],
                    installed_plugins: ["uploads"]
                }
            }
        };

        const c: t.NavigationContext = {
            APP: window.App,
            actionHandler: {
                silentFetch: jest.fn().mockResolvedValue({ suggestions: [] })
            },
            mentionValues: {
                "@": [{ value: "Mention @People" }],
                "#": [{ value: "Tag #content" }]
            }
        };
        const parent = {
            getValue: () => { return valueRef.current; },
            leafIndexMatch: () => { return true; },
            dataKey: "testKey",
            props: { elem: { name: "testParent" } },
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            update: (values: any) => { valueRef.current = values['testKey']; },
        };

        
        const toolbarContainer = document.createElement("div");
        const props = {
            c, parent,
            plain: false,
            showHeader: true,
            inGrid: false,
        }
        const qm = getQuillModules({
            signal: null,
            i18n,
            props,
            quillRef: React.createRef<Quill>()
        });

        qm.modules.toolbar = toolbarContainer;
        modules = qm.modules;
    });

    beforeEach(() => {
        valueRef.current = "";
        quillContainer = document.createElement("div");

        quill = new Quill(quillContainer, {
            modules,
            theme: 'snow'
        });

        expect(quill).toBeDefined();
    });

    it("should render Quill editor", async () => {
        valueRef.current = `
            <table class="table">
                <tbody>
                    <tr>
                        <td data-row="row-4uol">Märkus: Detsembris <em>ei ole</em> Kaarli kirikus palvusi esmaspäeviti, sest kirikus toimuvad kontsertid. Selle asemel palvetame Dominiiklaste kabelis (<strong>Müürivahe 33</strong>). Ka proov kell 17 sealsamas. Ja <strong>5. jaanuaril 2025</strong> läheb elu edasi Kaarli kirikus.</td>
                    </tr>
                </tbody>
            </table>
            <p><br></p>
            <p><br></p>
            <p class="ql-align-center"><a href="https://commons.wikimedia.org/wiki/File:Tallinn_asv2022-04_img12_StCharles_Church.jpg" rel="noopener noreferrer" target="_blank"><span class="ql-image-align-right" contenteditable="false" style="--resize-width: 30%;" data-relative-size="true"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Tallinn_asv2022-04_img12_StCharles_Church.jpg/256px-Tallinn_asv2022-04_img12_StCharles_Church.jpg" data-blot-align="right" width="30%" alt="Saint Charles church, Tallinn, Estonia, 2022-04" height="auto"></span></a><br class="soft-break">(Foto: A.Savin, FAL, Wikimedia Commonsi kaudu)</p>
            <p><a href="https://www.laudate.ee/prayers/#common-prayer" rel="noopener noreferrer" target="_blank">Ühispalvus</a>igal esmaspäeval kell 18:00. Enne palvust kell 17:00 lauluproov ja ettevalmistused. Igaüks on teretulnud! Ootame lauljaid juurde!</p>
            <p>Asukoht: <a href="https://et.wikipedia.org/wiki/Tallinna_Kaarli_kirik" rel="noopener noreferrer" target="_blank">Tallinna Kaarli kirik</a></p>
            <p>Korraldaja: <a href="https://www.kaarlikogudus.ee/" rel="noopener noreferrer" target="_blank">EELK Tallinna Kaarli kogudus</a></p>
            <p>Kontakt: Annely Neame (5267825)</p>
            <p>N.B.: Juulis, augustis ja detsembris Kaarli kirikus palvusi esmaspäeviti <strong>ei ole</strong>.</p>`;

        const delta = quill.clipboard.convert({html: valueRef.current});
        
        const deltaStr = `
{
    "ops": [
        {
            "attributes": {
                "table-container": "table",
                "table": {
                    "row": "row-4uol"
                }
            },
            "insert": "Märkus: Detsembris "
        },
        {
            "attributes": {
                "table-container": "table",
                "table": {
                    "row": "row-4uol"
                },
                "italic": true
            },
            "insert": "ei ole"
        },
        {
            "attributes": {
                "table-container": "table",
                "table": {
                    "row": "row-4uol"
                }
            },
            "insert": " Kaarli kirikus palvusi esmaspäeviti, sest kirikus toimuvad kontsertid. Selle asemel palvetame Dominiiklaste kabelis ("
        },
        {
            "attributes": {
                "table-container": "table",
                "table": {
                    "row": "row-4uol"
                },
                "bold": true
            },
            "insert": "Müürivahe 33"
        },
        {
            "attributes": {
                "table-container": "table",
                "table": {
                    "row": "row-4uol"
                }
            },
            "insert": "). Ka proov kell 17 sealsamas. Ja "
        },
        {
            "attributes": {
                "table-container": "table",
                "table": {
                    "row": "row-4uol"
                },
                "bold": true
            },
            "insert": "5. jaanuaril 2025"
        },
        {
            "attributes": {
                "table-container": "table",
                "table": {
                    "row": "row-4uol"
                }
            },
            "insert": " läheb elu edasi Kaarli kirikus.\\n"
        },
        {
            "insert": "\\n\\n"
        },
        {
            "attributes": {
                "align": "center",
                "link": "https://commons.wikimedia.org/wiki/File:Tallinn_asv2022-04_img12_StCharles_Church.jpg",
                "imageAlign": {
                    "align": "right",
                    "title": "",
                    "width": "30%",
                    "contenteditable": "false",
                    "relativeSize": "true"
                },
                "alt": "Saint Charles church, Tallinn, Estonia, 2022-04",
                "height": "auto",
                "width": "30%"
            },
            "insert": {
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Tallinn_asv2022-04_img12_StCharles_Church.jpg/256px-Tallinn_asv2022-04_img12_StCharles_Church.jpg"
            }
        },
        {
            "attributes": {
                "align": "center"
            },
            "insert": " (Foto: A.Savin, FAL, Wikimedia Commonsi kaudu)\\n"
        },
        {
            "attributes": {
                "link": "https://www.laudate.ee/prayers/#common-prayer"
            },
            "insert": "Ühispalvus"
        },
        {
            "insert": "igal esmaspäeval kell 18:00. Enne palvust kell 17:00 lauluproov ja ettevalmistused. Igaüks on teretulnud! Ootame lauljaid juurde!\\nAsukoht: "
        },
        {
            "attributes": {
                "link": "https://et.wikipedia.org/wiki/Tallinna_Kaarli_kirik"
            },
            "insert": "Tallinna Kaarli kirik"
        },
        {
            "insert": "\\nKorraldaja: "
        },
        {
            "attributes": {
                "link": "https://www.kaarlikogudus.ee/"
            },
            "insert": "EELK Tallinna Kaarli kogudus"
        },
        {
            "insert": "\\nKontakt: Annely Neame (5267825)\\nN.B.: Juulis, augustis ja detsembris Kaarli kirikus palvusi esmaspäeviti "
        },
        {
            "attributes": {
                "bold": true
            },
            "insert": "ei ole"
        },
        {
            "insert": "."
        }
    ]
}`;
        // Normalize Unicode line separators to regular spaces for comparison
        const actualStr = JSON.stringify(delta, null, 4).trim().replace(/\u2028/g, ' ');
        const expectedStr = deltaStr.trim();
        
        expect(actualStr).toBe(expectedStr);

        quill.setContents(delta);

        expect(quillContainer.children[0].innerHTML).toEqual(
            valueRef.current
            .replace(/\n\s*/g, '')
            .replace('--resize-width: 30%;', '--resize-width: 0px;')
            .replace('data-relative-size="true"', 'data-relative-size="false"')
        );
    });

    describe.only('textbox', () => {
        it('inserting textbox', () => {
            valueRef.current = `
                <div class="ql-textbox" data-textbox="true" data-textbox-id="textbox-gbs4" style="width: 50%;" data-width="50%">
                    <p class="ql-textbox-block" data-textbox-id="textbox-gbs4">How did that foo got bar?</p>
                </div>`;
            let delta = quill.clipboard.convert({html: valueRef.current});

            expect(JSON.stringify(delta)).toBe(
                `{"ops":[{"insert":"How did that foo got bar?\\n","attributes":{"textbox":{"width":"50%","id":"textbox-gbs4"},"textbox-block":"textbox-gbs4"}}]}`
            );

            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            expect((delta.ops[0].attributes.textbox as any).id).toBe('textbox-gbs4');

            quill.setContents(delta);

            const html = quillContainer.children[0].innerHTML;
            const expectedBase = valueRef.current.replace(/\n\s*/g, '');
            expect(html).toEqual(expectedBase);

            // Insert a second textbox
            // We need a separator newline to force creation of a new block
            const newTextboxId = textboxId();
            delta = new Delta()
                .retain(quill.getLength())
                .insert('\n', {
                    'textbox': {
                        width: '50%',
                        align: '',
                        id: newTextboxId
                    },
                    'textbox-block': newTextboxId
                });

            quill.updateContents(delta);

            const updatedHtml = quillContainer.children[0].innerHTML;

            // Verify both textboxes exist
            expect(updatedHtml).toContain('data-textbox-id="textbox-gbs4"');
            expect(updatedHtml).toContain(`data-textbox-id="${newTextboxId}"`);
        });

        it('side-by-side textboxes', () => {
            // Create side-by-side textboxes WITHOUT a separator - split logic should handle it
            const leftId = textboxId();
            const rightId = textboxId();
            
            const delta = new Delta()
                .insert('Left box content\n', {
                    'textbox': {
                        width: '45%',
                        align: 'left',
                        id: leftId
                    },
                    'textbox-block': leftId
                })
                // No separator - the split logic should separate them
                .insert('Right box content\n', {
                    'textbox': {
                        width: '45%',
                        align: 'right',
                        id: rightId
                    },
                    'textbox-block': rightId
                });
            
            quill.setContents(delta);

            const html = quillContainer.children[0].innerHTML;

            // Verify both textboxes exist with proper alignment classes
            expect(html).toContain('ql-textbox-align-left');
            expect(html).toContain('ql-textbox-align-right');
            expect(html).toContain('Left box content');
            expect(html).toContain('Right box content');
            
            // Both should be 45% width to fit side-by-side
            const widthMatches = html.match(/width: 45%/g);
            expect(widthMatches?.length).toBeGreaterThanOrEqual(2);
            
            // Verify alignment attributes are preserved
            expect(html).toContain('data-align="left"');
            expect(html).toContain('data-align="right"');
            
            // Should NOT have a separator paragraph - textboxes should be adjacent
            expect(html).not.toContain('<p><br></p>');
        });

        it('loading side-by-side textboxes', async () => {
            valueRef.current = `
                <div class="ql-textbox ql-textbox-align-left" data-textbox="true" data-textbox-id="textbox-left" style="width: 45%;" data-width="45%" data-align="left">
                    <p class="ql-textbox-block" data-textbox-id="textbox-left">Left box content</p>
                </div>
                <div class="ql-textbox ql-textbox-align-right" data-textbox="true" data-textbox-id="textbox-right" style="width: 45%;" data-width="45%" data-align="right">
                    <p class="ql-textbox-block" data-textbox-id="textbox-right">Right box content</p>
                </div>`;
            const delta = quill.clipboard.convert({html: valueRef.current});

            expect(JSON.stringify(delta)).toBe(
                `{"ops":[{"insert":"Left box content\\n","attributes":{"textbox":{"width":"45%","align":"left","id":"textbox-left"},"textbox-block":"textbox-left"}},{"insert":"Right box content\\n","attributes":{"textbox":{"width":"45%","align":"right","id":"textbox-right"},"textbox-block":"textbox-right"}}]}`
            );

            quill.setContents(delta);

            const html = quillContainer.children[0].innerHTML;
            const expectedBase = valueRef.current.replace(/\n\s*/g, '');
            expect(html === expectedBase).toBe(true);
        });

        it('deleting from textbox', () => {
            // Start with a textbox
            const textboxIdValue = textboxId();
            const delta = new Delta()
                .insert('Content to delete\n', {
                    'textbox': {
                        width: '50%',
                        align: '',
                        id: textboxIdValue
                    },
                    'textbox-block': textboxIdValue
                });
            quill.setContents(delta);

            // Select part of the content to delete
            quill.setSelection(8, 6); // Select "to del"

            // Perform deletion
            quill.deleteText(8, 6, 'user');

            const html = quillContainer.children[0].innerHTML;

            expect(html).toContain('Content ete');
            expect(html).not.toContain('to del');
            expect(html).toContain('data-textbox-id="' + textboxIdValue + '"');
            const matches = html.match(new RegExp(`data-textbox-id="${textboxIdValue}"`, 'g'));
            expect(matches?.length).toBe(2);
        });
    });
});