# schemas

These are schemas one can use to validate objects used in the Fediverse.

## Schemas from other specifications

| schema | test page |
| --- | --- |
| [application/jrd+json](./assets/application-jrd-json.schema.json) | [Test Page](./application-jrd-json.md) |


## Old stuff

!!! warning
    Under construction

| schema | types | comment |
| --- | --- | --- |
| [follower_activity.schema](./follower_activity.schema.json) | `Follow`, `Reject`, `Accept`, `Undo`, `Block` | Currently object must be a string. Might be relaxed to also allow object |
| [audio_single.schema](./audio_single.schema.json) | `Audio` | Single URL version |
| [image_single.schema](./image_single.schema.json)| `Image` | Single URL version |
| [video_single.schema](./video_single.schema.json)| `Video` | Single URL version |
| [media_attachments.schema](./media_attachments.schema.json) | `Audio`, `Image`, `Video` |the more complicated version of the image_single, etc ... files. Not really readable. Also includes multiple urls. |

!!! info
    Contributions of new schemas are welcome; see repo.
