#!/usr/bin/python
# -*- coding: utf-8 -*-

#import base64
import os
from rivista.interface.xmpp.avatar import InterfaceXmppAvatar
from rivista.interface.xmpp.client import InterfaceXmppClient
from rivista.interface.xmpp.ping import InterfaceXmppPing
from rivista.interface.xmpp.vcard import InterfaceXmppVCard
from rivista.parser.toml import ParserToml
from rivista.property.publish import publish_properties
from rivista.utility.config import Data
from rivista.utility.logger import UtilityLogger
from rivista.utility.qr import UtilityQR
import sys

logger = UtilityLogger(__name__)

class UtilityVCard:

    async def cache():
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        address = publish_properties.address
        password = publish_properties.password
        xmpp_instance = InterfaceXmppClient(address, password)
        rtt = await InterfaceXmppPing.to_self(xmpp_instance)
        if xmpp_instance.is_connected or rtt:
            xep, iq = await InterfaceXmppVCard.retrieve(xmpp_instance)
            if xep:
                if xep == "0292":
                    # NOTE for i in iq["pubsub"]["items"]["item"]["payload"].itertext(): i
                    iq_pubsub_vcard = iq["pubsub"]["items"]["item"]["vcard"]
                    vcard = {
                        "birthday" : iq_pubsub_vcard["birthday"] or "",
                        "name" : iq_pubsub_vcard["fn"]["text"] or iq_pubsub_vcard["full_name"] or "",
                        #"N" : iq_pubsub_vcard["n"] or "",
                        "alias" : iq_pubsub_vcard["nickname"]["text"] or "",
                        "note" : iq_pubsub_vcard["note"]["text"] or "",
                        #"PHOTO" : base64.b64encode(vcard_temp["PHOTO"]["BINVAL"]).decode("utf-8"),
                        "role" : "",
                        "url" : iq_pubsub_vcard["url"]["uri"] or "",
                        "version" : iq["pubsub"]["items"]["node"] or "",
                    }
                    vcard_image_binary = await InterfaceXmppAvatar.retrieve(xmpp_instance)
                elif xep == "0054":
                    iq_vcard_temp = iq["vcard_temp"]
                    vcard = {
                        "birthday" : iq_vcard_temp["BDAY"] or "",
                        "name" : iq_vcard_temp["FN"] or "",
                        #"N" : iq_vcard_temp["N"] or "",
                        "alias" : iq_vcard_temp["NICKNAME"][0] if iq_vcard_temp["NICKNAME"] else "",
                        "note" : iq_vcard_temp["NOTE"] or "",
                        #"PHOTO" : base64.b64encode(vcard_temp["PHOTO"]["BINVAL"]).decode("utf-8"),
                        "role" : iq_vcard_temp["ROLE"] or "",
                        "url" : iq_vcard_temp["URL"] or "",
                        "version" : iq_vcard_temp["VERSION"] or "",
                        #"birthdays" : iq_vcard_temp["birthdays"],
                        #"lang" : iq_vcard_temp["lang"],
                        #"nicknames" : iq_vcard_temp["nicknames"],
                        #"notes" : iq_vcard_temp["notes"],
                        #"photos" : iq_vcard_temp["photos"],
                        #"roles" : iq_vcard_temp["roles"],
                        #"urls" : iq_vcard_temp["urls"],
                    }
                    vcard_image_binary = iq_vcard_temp["PHOTO"]["BINVAL"]
                directory_data = Data.get_directory()
                directory_profile = os.path.join(directory_data, "profile")
                if not os.path.exists(directory_profile):
                    os.mkdir(directory_profile)
                filename_vcard_toml = os.path.join(
                    directory_data, "xmpp", "vcard.toml")
                ParserToml.save_file(filename_vcard_toml, vcard)
                filename_qr_image = os.path.join(
                    directory_data, "profile", f"qr.png")
                jid_bare = xmpp_instance.boundjid.bare
                xmpp_uri = f"xmpp:{jid_bare}?message"
                UtilityQR.generate(xmpp_uri, filename_qr_image)
                if vcard_image_binary:
                    vcard_image_type = iq_vcard_temp["PHOTO"]["TYPE"]
                    vcard_image_extval = iq_vcard_temp["PHOTO"]["EXTVAL"]
                    filename_vcard_image = os.path.join(
                        directory_data, "profile", f"image")
                    with open(filename_vcard_image, "wb") as file:
                        file.write(vcard_image_binary)
                #filename_vcard_xml = os.path.join(
                #    directory_data, "vcard.xml")
                #with open(filename_vcard_xml, "wb") as file: file.write(iq.xml)
                #import xml.etree.ElementTree as ET
                #iq_xml = ET.tostring(iq.xml, encoding="utf-8", xml_declaration=True)
                #with open(filename_vcard_xml, "wb") as file: file.write(iq_xml)

                #PublishXml.contact(pathname, filename)
            #else:
