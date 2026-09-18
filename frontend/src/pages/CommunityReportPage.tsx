import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import {
  AIUnderstandingResponse,
  ExtractedItem
} from '../types';
import api from '../services/api';
import {
  Sparkles,
  Send,
  CheckCircle2,
  Edit2
} from 'lucide-react';
import { LocationPicker } from '../components/LocationPicker';

export const CommunityReportPage: React.FC = () => {
  const {
    showNotification,
    setActiveTab
  } = useApp();

  // ============================================================
  // NATURAL LANGUAGE INPUT
  // ============================================================

  const [nlText, setNlText] = useState(
    'Around 350 people are stranded in Village A. We urgently need drinking water, food and medicines. There are 40 elderly people and 25 children.'
  );

  const [parsing, setParsing] =
    useState(false);

  const [aiUnderstanding, setAiUnderstanding] =
    useState<AIUnderstandingResponse | null>(null);

  // ============================================================
  // FORM DATA
  // ============================================================

  const [locationName, setLocationName] =
    useState('');

  // Coordinates are internal application data.
  // The user never types these manually.
  const [locationLatitude, setLocationLatitude] =
    useState<number | null>(null);

  const [locationLongitude, setLocationLongitude] =
    useState<number | null>(null);

  const [affectedPeople, setAffectedPeople] =
    useState(350);

  const [affectedHouseholds, setAffectedHouseholds] =
    useState(85);

  const [vulnerableElderly, setVulnerableElderly] =
    useState(40);

  const [vulnerableChildren, setVulnerableChildren] =
    useState(25);

  const [urgency, setUrgency] =
    useState('CRITICAL');

  const [reporterName, setReporterName] =
    useState('Sarpanch Ramesh');

  const [reporterPhone, setReporterPhone] =
    useState('+91 94812 33491');

  const [items, setItems] =
    useState<ExtractedItem[]>([
      {
        category: 'Drinking Water',
        item_name: 'Clean Drinking Water',
        quantity: 2000,
        unit: 'Liters'
      },
      {
        category: 'Food',
        item_name: 'Ready-to-Eat Food Packets',
        quantity: 700,
        unit: 'Packets'
      },
      {
        category: 'Medicines',
        item_name: 'Emergency Medicine Kits',
        quantity: 35,
        unit: 'Kits'
      }
    ]);

  // ============================================================
  // SUBMISSION STATE
  // ============================================================

  const [submittedCode, setSubmittedCode] =
    useState<string | null>(null);

  const [submitting, setSubmitting] =
    useState(false);

  // ============================================================
  // AI PARSING
  // ============================================================

  const handleParseNLP = async () => {
    if (!nlText.trim()) {
      showNotification(
        'Please describe the situation first.',
        'error'
      );
      return;
    }

    setParsing(true);

    try {
      const parsed =
        await api.parseNLP(nlText);

      setAiUnderstanding(parsed);

      // AI can provide a textual location.
      setLocationName(
        parsed.extracted_location || ''
      );

      // If the AI was able to determine coordinates,
      // use them automatically.
      if (
        parsed.latitude !== undefined &&
        parsed.latitude !== null
      ) {
        setLocationLatitude(
          parsed.latitude
        );
      }

      if (
        parsed.longitude !== undefined &&
        parsed.longitude !== null
      ) {
        setLocationLongitude(
          parsed.longitude
        );
      }

      setAffectedPeople(
        parsed.affected_people
      );

      setAffectedHouseholds(
        parsed.affected_households
      );

      setVulnerableElderly(
        parsed.vulnerable_elderly
      );

      setVulnerableChildren(
        parsed.vulnerable_children
      );

      setUrgency(
        parsed.urgency
      );

      if (parsed.items.length > 0) {
        setItems(
          parsed.items
        );
      }

      showNotification(
        'AI parsed your description into structured relief requirements.',
        'success'
      );

    } catch (error) {
      console.error(
        'AI parsing failed:',
        error
      );

      showNotification(
        'Failed to parse text with AI.',
        'error'
      );

    } finally {
      setParsing(false);
    }
  };

  // ============================================================
  // SUBMIT REQUEST
  // ============================================================

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    // Location is mandatory.
    // The user selects it through the map/search picker.
    if (
      locationLatitude === null ||
      locationLongitude === null ||
      !locationName.trim()
    ) {
      showNotification(
        'Please select the affected location on the map before submitting.',
        'error'
      );

      return;
    }

    if (
      affectedPeople < 1
    ) {
      showNotification(
        'Affected people must be at least 1.',
        'error'
      );

      return;
    }

    if (
      items.length === 0
    ) {
      showNotification(
        'Please specify at least one required relief item.',
        'error'
      );

      return;
    }

    setSubmitting(true);

    try {
      const res =
        await api.createRequest({
          location_name:
            locationName.trim(),

          // Automatically captured from the map.
          latitude:
            locationLatitude,

          longitude:
            locationLongitude,

          affected_people:
            Number(affectedPeople),

          affected_households:
            Number(affectedHouseholds),

          vulnerable_elderly:
            Number(vulnerableElderly),

          vulnerable_children:
            Number(vulnerableChildren),

          urgency:
            urgency,

          raw_description:
            nlText.trim(),

          reporter_name:
            reporterName.trim(),

          reporter_phone:
            reporterPhone.trim(),

          items:
            items.map(item => ({
              category:
                item.category,

              item_name:
                item.item_name,

              requested_quantity:
                Number(
                  item.quantity
                ),

              unit:
                item.unit
            }))
        });

      setSubmittedCode(
        res.tracking_code
      );

      showNotification(
        `Request ${res.tracking_code} submitted! Prioritized with score ${res.priority_score}/100.`,
        'success'
      );

    } catch (error) {
      console.error(
        'Relief request submission failed:',
        error
      );

      const message =
        error instanceof Error
          ? error.message
          : 'Failed to submit relief request.';

      showNotification(
        message,
        'error'
      );

    } finally {
      setSubmitting(false);
    }
  };

  // ============================================================
  // SUCCESS SCREEN
  // ============================================================

  if (submittedCode) {
    return (
      <div className="
        max-w-2xl
        mx-auto
        py-16
        px-4
        text-center
      ">

        <div className="
          bg-ivory
          border
          border-slate/20
          rounded-2xl
          p-8
          shadow-elevated
        ">

          <div className="
            w-16
            h-16
            rounded-full
            bg-emerald-100
            text-status-fulfilled
            flex
            items-center
            justify-center
            mx-auto
            mb-4
          ">
            <CheckCircle2 className="
              w-10
              h-10
            " />
          </div>

          <h2 className="
            text-2xl
            font-extrabold
            text-navy
          ">
            Relief Request Logged Successfully
          </h2>

          <p className="
            text-slate
            text-sm
            mt-2
          ">
            Your emergency report has been
            routed to the emergency operations
            workflow and nearby relief resources.
          </p>

          <div className="
            my-6
            p-4
            bg-ivory-100
            rounded-xl
            border
            border-slate/20
            inline-block
          ">

            <div className="
              text-xs
              uppercase
              tracking-wider
              text-slate
              font-semibold
            ">
              Your Request Tracking Code
            </div>

            <div className="
              text-3xl
              font-mono
              font-extrabold
              text-terracotta
              mt-1
            ">
              {submittedCode}
            </div>

          </div>

          <div className="
            text-xs
            text-slate
            mb-6
          ">
            The request can now be reviewed,
            prioritized, mapped and matched
            with available relief resources.
          </div>

          <div className="
            flex
            justify-center
            gap-3
          ">

            <button
              type="button"
              onClick={() => {
                setSubmittedCode(null);

                setLocationName('');
                setLocationLatitude(null);
                setLocationLongitude(null);

                setAiUnderstanding(null);
              }}
              className="
                bg-ivory
                border
                border-slate/30
                text-navy
                font-semibold
                px-4
                py-2
                rounded-lg
                text-xs
                hover:bg-slate/10
              "
            >
              Report Another Need
            </button>

            <button
              type="button"
              onClick={() =>
                setActiveTab('command')
              }
              className="
                bg-navy
                hover:bg-navy-800
                text-white
                font-semibold
                px-4
                py-2
                rounded-lg
                text-xs
              "
            >
              View Operations Map
            </button>

          </div>

        </div>

      </div>
    );
  }

  // ============================================================
  // MAIN REPORT PAGE
  // ============================================================

  return (
    <div className="
      max-w-4xl
      mx-auto
      px-4
      sm:px-6
      py-6
      space-y-8
    ">

      {/* ======================================================
          PAGE TITLE
      ======================================================= */}

      <div>

        <h1 className="
          text-2xl
          sm:text-3xl
          font-extrabold
          text-navy
          tracking-tight
        ">
          Report a Flood Relief Need
        </h1>

        <p className="
          text-xs
          sm:text-sm
          text-slate
          mt-1
        ">
          Describe the emergency in your own
          words, select the affected location,
          and submit the request for relief
          coordination.
        </p>

      </div>

      {/* ======================================================
          STEP 1: NATURAL LANGUAGE DESCRIPTION
      ======================================================= */}

      <div className="
        bg-ivory
        border
        border-slate/20
        rounded-xl
        p-6
        shadow-soft
      ">

        <div className="
          flex
          items-center
          justify-between
          mb-2
        ">

          <label className="
            text-sm
            font-bold
            text-navy
            flex
            items-center
            gap-1.5
          ">

            <Sparkles className="
              w-4
              h-4
              text-terracotta
            " />

            <span>
              Describe the Situation Naturally
            </span>

          </label>

          <span className="
            text-xs
            text-slate
          ">
            AI extracts location,
            population and supplies
          </span>

        </div>

        <textarea
          rows={3}
          value={nlText}
          onChange={e =>
            setNlText(
              e.target.value
            )
          }
          placeholder="
            e.g. Around 350 people are
            stranded in Village A...
          "
          className="
            w-full
            bg-white
            border
            border-slate/30
            rounded-lg
            p-3
            text-xs
            sm:text-sm
            text-navy
            focus:outline-none
            focus:border-terracotta
            shadow-inner
          "
        />

        <div className="
          mt-3
          flex
          items-center
          justify-between
          gap-4
        ">

          <div className="
            text-[11px]
            text-slate
            italic
          ">
            Mention the affected area,
            number of people, vulnerable
            groups and urgently required
            supplies.
          </div>

          <button
            type="button"
            onClick={
              handleParseNLP
            }
            disabled={parsing}
            className="
              bg-navy
              hover:bg-navy-800
              text-white
              font-semibold
              px-4
              py-2
              rounded-lg
              text-xs
              flex
              items-center
              space-x-1.5
              shadow-sm
              transition-colors
              disabled:opacity-50
              whitespace-nowrap
            "
          >

            <Sparkles className="
              w-3.5
              h-3.5
              text-terracotta
            " />

            <span>
              {
                parsing
                  ? 'Parsing with AI...'
                  : 'Parse with AI'
              }
            </span>

          </button>

        </div>

        {/* ==================================================
            AI UNDERSTANDING
        =================================================== */}

        {aiUnderstanding && (
          <div className="
            mt-4
            p-4
            bg-terracotta-50
            border
            border-terracotta/30
            rounded-lg
            text-xs
          ">

            <div className="
              font-bold
              text-navy
              flex
              items-center
              justify-between
              mb-1.5
            ">

              <span className="
                text-terracotta
                uppercase
                tracking-wider
                text-[11px]
              ">
                AI UNDERSTANDING
              </span>

              <span className="
                text-slate
                font-mono
                text-[10px]
              ">
                Confidence:
                {' '}
                {Math.round(
                  aiUnderstanding.confidence_score *
                  100
                )}
                %
              </span>

            </div>

            <div className="
              grid
              grid-cols-2
              sm:grid-cols-4
              gap-2
              text-slate-dark
            ">

              <div>
                Location:
                {' '}
                <b>
                  {
                    aiUnderstanding
                      .extracted_location
                  }
                </b>
              </div>

              <div>
                Affected:
                {' '}
                <b>
                  {
                    aiUnderstanding
                      .affected_people
                  } people
                </b>
              </div>

              <div>
                Vulnerable:
                {' '}
                <b>
                  {
                    aiUnderstanding
                      .vulnerable_total
                  } people
                </b>
              </div>

              <div>
                Urgency:
                {' '}
                <b className="
                  text-red-700
                ">
                  {
                    aiUnderstanding.urgency
                  }
                </b>
              </div>

            </div>

            <div className="
              mt-2
              text-[11px]
              text-slate
              border-t
              border-terracotta/20
              pt-1.5
            ">

              <b>
                Identified Supplies:
              </b>

              {' '}

              {
                aiUnderstanding.items
                  .map(
                    item =>
                      `${item.quantity} ${item.unit} ${item.category}`
                  )
                  .join(', ')
              }

            </div>

          </div>
        )}

      </div>

      {/* ======================================================
          STEP 2: CONFIRM & REFINE
      ======================================================= */}

      <form
        onSubmit={handleSubmit}
        className="
          bg-ivory
          border
          border-slate/20
          rounded-xl
          p-6
          shadow-soft
          space-y-6
        "
      >

        <h3 className="
          font-bold
          text-base
          text-navy
          pb-2
          border-b
          border-slate/15
          flex
          items-center
          gap-2
        ">

          <Edit2 className="
            w-4
            h-4
            text-terracotta
          " />

          <span>
            Confirm & Refine Request Details
          </span>

        </h3>

        <div className="
          grid
          grid-cols-1
          sm:grid-cols-2
          gap-4
          text-xs
        ">

          {/* ==================================================
              LOCATION PICKER
          =================================================== */}

          <div className="
            sm:col-span-2
          ">

            <LocationPicker
              locationName={
                locationName
              }

              latitude={
                locationLatitude
              }

              longitude={
                locationLongitude
              }

              onLocationChange={(
                name,
                latitude,
                longitude
              ) => {
                setLocationName(
                  name
                );

                setLocationLatitude(
                  latitude
                );

                setLocationLongitude(
                  longitude
                );
              }}
            />

          </div>

          {/* ==================================================
              URGENCY
          =================================================== */}

          <div>

            <label className="
              block
              font-semibold
              text-slate-dark
              mb-1
            ">
              Assessed Urgency Level
            </label>

            <select
              value={urgency}
              onChange={e =>
                setUrgency(
                  e.target.value
                )
              }
              className="
                w-full
                bg-white
                border
                border-slate/30
                rounded-lg
                px-3
                py-2
                text-navy
                font-semibold
              "
            >

              <option value="CRITICAL">
                CRITICAL (Immediate Life Threat)
              </option>

              <option value="HIGH">
                HIGH (Urgent Assistance Required)
              </option>

              <option value="MEDIUM">
                MEDIUM (Stable / Need Support)
              </option>

              <option value="LOW">
                LOW (Monitoring / Non-critical)
              </option>

            </select>

          </div>

          {/* ==================================================
              AFFECTED PEOPLE
          =================================================== */}

          <div>

            <label className="
              block
              font-semibold
              text-slate-dark
              mb-1
            ">
              Total Stranded / Affected People
            </label>

            <input
              type="number"
              min="1"
              value={
                affectedPeople
              }
              onChange={e =>
                setAffectedPeople(
                  Number(
                    e.target.value
                  )
                )
              }
              className="
                w-full
                bg-white
                border
                border-slate/30
                rounded-lg
                px-3
                py-2
                text-navy
              "
            />

          </div>

          {/* ==================================================
              HOUSEHOLDS
          =================================================== */}

          <div>

            <label className="
              block
              font-semibold
              text-slate-dark
              mb-1
            ">
              Households Affected
            </label>

            <input
              type="number"
              min="1"
              value={
                affectedHouseholds
              }
              onChange={e =>
                setAffectedHouseholds(
                  Number(
                    e.target.value
                  )
                )
              }
              className="
                w-full
                bg-white
                border
                border-slate/30
                rounded-lg
                px-3
                py-2
                text-navy
              "
            />

          </div>

          {/* ==================================================
              ELDERLY
          =================================================== */}

          <div>

            <label className="
              block
              font-semibold
              text-slate-dark
              mb-1
            ">
              Elderly Individuals
            </label>

            <input
              type="number"
              min="0"
              value={
                vulnerableElderly
              }
              onChange={e =>
                setVulnerableElderly(
                  Number(
                    e.target.value
                  )
                )
              }
              className="
                w-full
                bg-white
                border
                border-slate/30
                rounded-lg
                px-3
                py-2
                text-navy
              "
            />

          </div>

          {/* ==================================================
              CHILDREN
          =================================================== */}

          <div>

            <label className="
              block
              font-semibold
              text-slate-dark
              mb-1
            ">
              Children & Infants
            </label>

            <input
              type="number"
              min="0"
              value={
                vulnerableChildren
              }
              onChange={e =>
                setVulnerableChildren(
                  Number(
                    e.target.value
                  )
                )
              }
              className="
                w-full
                bg-white
                border
                border-slate/30
                rounded-lg
                px-3
                py-2
                text-navy
              "
            />

          </div>

          {/* ==================================================
              REPORTER NAME
          =================================================== */}

          <div>

            <label className="
              block
              font-semibold
              text-slate-dark
              mb-1
            ">
              Reporter / Coordinator Name
            </label>

            <input
              type="text"
              value={
                reporterName
              }
              onChange={e =>
                setReporterName(
                  e.target.value
                )
              }
              className="
                w-full
                bg-white
                border
                border-slate/30
                rounded-lg
                px-3
                py-2
                text-navy
              "
            />

          </div>

          {/* ==================================================
              PHONE
          =================================================== */}

          <div>

            <label className="
              block
              font-semibold
              text-slate-dark
              mb-1
            ">
              Contact Phone Number
            </label>

            <input
              type="text"
              value={
                reporterPhone
              }
              onChange={e =>
                setReporterPhone(
                  e.target.value
                )
              }
              className="
                w-full
                bg-white
                border
                border-slate/30
                rounded-lg
                px-3
                py-2
                text-navy
              "
            />

          </div>

        </div>

        {/* ======================================================
            REQUESTED SUPPLIES
        ======================================================= */}

        <div>

          <label className="
            block
            font-bold
            text-navy
            text-xs
            mb-2
          ">
            Requested Supplies
          </label>

          <div className="
            space-y-2
          ">

            {items.map(
              (item, index) => (
                <div
                  key={index}
                  className="
                    flex
                    items-center
                    gap-2
                    text-xs
                  "
                >

                  <input
                    type="text"
                    value={
                      item.category
                    }
                    readOnly
                    className="
                      w-1/3
                      bg-ivory-100
                      border
                      border-slate/20
                      rounded
                      px-2.5
                      py-1.5
                      font-medium
                      text-navy
                    "
                  />

                  <input
                    type="text"
                    value={
                      item.item_name
                    }
                    onChange={e => {
                      const updated =
                        [...items];

                      updated[index] = {
                        ...updated[index],
                        item_name:
                          e.target.value
                      };

                      setItems(
                        updated
                      );
                    }}
                    className="
                      flex-1
                      bg-white
                      border
                      border-slate/30
                      rounded
                      px-2.5
                      py-1.5
                      text-navy
                    "
                  />

                  <input
                    type="number"
                    min="0"
                    value={
                      item.quantity
                    }
                    onChange={e => {
                      const updated =
                        [...items];

                      updated[index] = {
                        ...updated[index],
                        quantity:
                          Number(
                            e.target.value
                          )
                      };

                      setItems(
                        updated
                      );
                    }}
                    className="
                      w-24
                      bg-white
                      border
                      border-slate/30
                      rounded
                      px-2.5
                      py-1.5
                      text-navy
                      font-bold
                    "
                  />

                  <span className="
                    w-16
                    text-slate
                    font-medium
                  ">
                    {item.unit}
                  </span>

                </div>
              )
            )}

          </div>

        </div>

        {/* ======================================================
            SUBMIT
        ======================================================= */}

        <div className="
          pt-4
          border-t
          border-slate/20
          flex
          justify-end
        ">

          <button
            type="submit"
            disabled={
              submitting
            }
            className="
              bg-terracotta
              hover:bg-terracotta-hover
              text-white
              font-bold
              px-6
              py-3
              rounded-lg
              shadow-card
              text-xs
              sm:text-sm
              flex
              items-center
              space-x-2
              transition-colors
              disabled:opacity-50
            "
          >

            <Send className="
              w-4
              h-4
            " />

            <span>
              {
                submitting
                  ? 'Submitting to Emergency Operations...'
                  : 'Submit Emergency Request'
              }
            </span>

          </button>

        </div>

      </form>

    </div>
  );
};